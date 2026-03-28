import os
import json
import subprocess
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global RAG state ───────────────────────────────────────────────────────────
vector_store: FAISS | None = None
indexed_files: list[str] = []

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_MAP = {
    "gpt-4o-mini":   ("openai",  "gpt-4o-mini"),
    "gpt-4o":        ("openai",  "gpt-4o"),
    "llama3.2":      ("ollama",  "llama3.2"),
    "llama3.1":      ("ollama",  "llama3.1"),
    "codellama":     ("ollama",  "codellama"),
}

TASK_PROMPTS = {
    "write": (
        "You are an expert software engineer and GitHub Copilot-style assistant. "
        "Write clean, efficient, and production-ready code. Use best practices, "
        "add necessary comments, and explain your implementation clearly. "
        "Always wrap code in fenced blocks with the correct language identifier."
    ),
    "debug": (
        "You are an expert debugger. Carefully analyse the provided code, "
        "identify all bugs and root causes with explanations, then provide "
        "the fully corrected code with clear explanations of each fix."
    ),
    "explain": (
        "You are a patient code educator. Explain the code clearly — what it does, "
        "how it works, key concepts, and notable patterns. Tailor depth to the context."
    ),
    "optimize": (
        "You are a performance optimisation expert. Find bottlenecks, redundancies, "
        "and readability issues. Provide optimised code and explain every improvement."
    ),
    "review": (
        "You are a senior code reviewer. Cover code quality, best practices, potential "
        "bugs, security issues, performance, and maintainability. Be specific and constructive."
    ),
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_llm(model_key: str):
    provider, model_id = MODEL_MAP.get(model_key, ("openai", "gpt-4o-mini"))
    if provider == "openai":
        return ChatOpenAI(model=model_id, temperature=0, streaming=True)
    # Ollama runs locally — no API key needed
    return ChatOllama(model=model_id, temperature=0)


def get_rag_context(query: str) -> str:
    if vector_store is None:
        return ""
    docs = vector_store.similarity_search(query, k=3)
    snippets = "\n\n".join(
        f"[{d.metadata['source']}]\n{d.page_content}" for d in docs
    )
    return f"\n\nRelevant context from uploaded files:\n{snippets}"


def build_history(raw: list[dict]):
    history = []
    for m in raw:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        history.append(cls(content=m["content"]))
    return history

# ── Schemas ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    input: str
    model: str = "gpt-4o-mini"
    language: str = "Auto-detect"
    task: str = "write"
    history: list[dict] = []


class ExecuteRequest(BaseModel):
    code: str

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    full_input = req.input
    if req.language != "Auto-detect":
        full_input = f"[Target language: {req.language}]\n\n{req.input}"

    system_prompt = TASK_PROMPTS.get(req.task, TASK_PROMPTS["write"])
    system_prompt += get_rag_context(req.input)

    history = build_history(req.history)
    llm = get_llm(req.model)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    chain = prompt | llm | StrOutputParser()

    async def generate():
        try:
            async for chunk in chain.astream({"input": full_input, "chat_history": history}):
                yield f"data: {json.dumps({'token': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    global vector_store, indexed_files
    content = (await file.read()).decode("utf-8", errors="ignore")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([content], metadatas=[{"source": file.filename}])
    embeddings = OpenAIEmbeddings()
    if vector_store is None:
        vector_store = FAISS.from_documents(docs, embeddings)
    else:
        vector_store.add_documents(docs)
    if file.filename not in indexed_files:
        indexed_files.append(file.filename)
    return {"status": "indexed", "file": file.filename, "chunks": len(docs)}


@app.delete("/api/context")
async def clear_context():
    global vector_store, indexed_files
    vector_store = None
    indexed_files = []
    return {"status": "cleared"}


@app.get("/api/files")
async def list_files():
    return {"files": indexed_files}


@app.post("/api/execute")
async def execute(req: ExecuteRequest):
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(req.code)
        tmp = f.name
    try:
        result = subprocess.run(
            ["python3", tmp], capture_output=True, text=True, timeout=10
        )
        output = result.stdout or result.stderr or "(no output)"
    except subprocess.TimeoutExpired:
        output = "⏱ Timed out (10 s limit)"
    except Exception as e:
        output = f"Error: {e}"
    finally:
        os.unlink(tmp)
    return {"output": output}


# ── Serve React build in production ───────────────────────────────────────────
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
