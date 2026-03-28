import streamlit as st
import os
import subprocess
import tempfile
import re
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Coding Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GitHub Copilot Dark Theme CSS ──────────────────────────────────────────────
st.markdown("""
<style>
  /* Base */
  .stApp { background-color: #0d1117; color: #e6edf3; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
  }
  section[data-testid="stSidebar"] * { color: #e6edf3 !important; }

  /* Selectbox */
  .stSelectbox > div > div {
    background-color: #21262d !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 6px !important;
  }

  /* File uploader */
  [data-testid="stFileUploader"] {
    background-color: #161b22 !important;
    border: 1px dashed #30363d !important;
    border-radius: 6px;
  }

  /* Buttons */
  .stButton > button {
    background-color: #21262d !important;
    color: #58a6ff !important;
    border: 1px solid #388bfd !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background-color: #388bfd !important;
    color: #fff !important;
  }

  /* Chat messages */
  [data-testid="stChatMessage"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
  }

  /* Chat input */
  [data-testid="stChatInput"] textarea {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    font-family: 'Consolas', 'Monaco', monospace !important;
  }
  [data-testid="stChatInput"] {
    background-color: #0d1117 !important;
    border-top: 1px solid #30363d !important;
  }

  /* Code blocks */
  pre, code {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    color: #79c0ff !important;
  }

  /* Expander */
  [data-testid="stExpander"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
  }

  /* Headings & text */
  h1, h2, h3, h4, label, p, span, div { color: #e6edf3 !important; }
  hr { border-color: #30363d !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: #0d1117; }
  ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

  /* Success / error / warning */
  .stSuccess { background-color: #1a4731 !important; border-color: #2ea043 !important; }
  .stError   { background-color: #4d1e1e !important; border-color: #f85149 !important; }
  .stWarning { background-color: #3d2c00 !important; border-color: #d29922 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_OPTIONS = {
    "GPT-4o Mini  (fast)":    ("openai",     "gpt-4o-mini"),
    "GPT-4o  (powerful)":     ("openai",     "gpt-4o"),
    "Claude Sonnet 4.6":      ("anthropic",  "claude-sonnet-4-6"),
    "Claude Haiku 4.5":       ("anthropic",  "claude-haiku-4-5-20251001"),
}

LANGUAGE_OPTIONS = [
    "Auto-detect", "Python", "JavaScript", "TypeScript",
    "Go", "Rust", "Java", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin",
]

TASK_PROMPTS = {
    "✏️  Write Code": (
        "You are an expert software engineer and GitHub Copilot-style assistant. "
        "Write clean, efficient, and production-ready code. Use best practices, "
        "add necessary comments, and explain your implementation. "
        "Always wrap code in fenced blocks with the correct language identifier."
    ),
    "🐛  Debug": (
        "You are an expert debugger. Carefully analyse the provided code, "
        "identify all bugs and root causes, explain why each occurs, then provide "
        "fully corrected code with clear explanations."
    ),
    "📖  Explain": (
        "You are a patient code educator. Explain the code clearly — what it does, "
        "how it works, key concepts, and any notable patterns. Tailor depth to context."
    ),
    "⚡  Optimize": (
        "You are a performance optimisation expert. Find bottlenecks, redundancies, "
        "and readability issues. Provide optimised code and explain every improvement."
    ),
    "🔍  Review": (
        "You are a senior code reviewer. Cover code quality, best practices, potential "
        "bugs, security issues, performance, and maintainability. Be specific and constructive."
    ),
}

# ── Session State ──────────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "vector_store" not in st.session_state: st.session_state.vector_store = None
if "indexed_files" not in st.session_state: st.session_state.indexed_files = []

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_llm(model_key: str):
    provider, model_id = MODEL_OPTIONS[model_key]
    if provider == "openai":
        return ChatOpenAI(model=model_id, temperature=0, streaming=True)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY not found in .env — add it to use Claude models.")
        st.stop()
    return ChatAnthropic(model=model_id, temperature=0, streaming=True)


def build_chain(llm, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    return prompt | llm | StrOutputParser()


def get_history() -> list:
    """Return all messages except the last (which we're about to answer)."""
    msgs = st.session_state.messages
    history = []
    for m in msgs[:-1]:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        history.append(cls(content=m["content"]))
    return history


def extract_python_blocks(text: str) -> list[str]:
    return re.findall(r"```(?:python|py)\n(.*?)```", text, re.DOTALL)


def execute_python(code: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        result = subprocess.run(
            ["python3", tmp], capture_output=True, text=True, timeout=10
        )
        return result.stdout or result.stderr or "(no output)"
    except subprocess.TimeoutExpired:
        return "⏱ Timed out (10 s limit)"
    except Exception as e:
        return f"Error: {e}"
    finally:
        os.unlink(tmp)


def index_file(content: str, filename: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([content], metadatas=[{"source": filename}])
    embeddings = OpenAIEmbeddings()
    if st.session_state.vector_store is None:
        st.session_state.vector_store = FAISS.from_documents(docs, embeddings)
    else:
        st.session_state.vector_store.add_documents(docs)
    st.session_state.indexed_files.append(filename)


def get_rag_context(query: str) -> str:
    if st.session_state.vector_store is None:
        return ""
    docs = st.session_state.vector_store.similarity_search(query, k=3)
    snippets = "\n\n".join(
        f"[{d.metadata['source']}]\n{d.page_content}" for d in docs
    )
    return f"\n\nRelevant context from uploaded files:\n{snippets}"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    selected_model    = st.selectbox("🤖 Model",     list(MODEL_OPTIONS.keys()))
    selected_language = st.selectbox("🔤 Language",  LANGUAGE_OPTIONS)
    selected_task     = st.selectbox("🎯 Task Mode", list(TASK_PROMPTS.keys()))

    st.markdown("---")
    st.markdown("### 📁 Upload Code / Docs")
    uploaded = st.file_uploader(
        "Add files as RAG context",
        type=["py","js","ts","go","java","cpp","c","cs","md","txt","json"],
        accept_multiple_files=True,
    )
    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.indexed_files:
                content = f.read().decode("utf-8", errors="ignore")
                index_file(content, f.name)
                st.success(f"✅ Indexed: {f.name}")

    if st.session_state.indexed_files:
        st.markdown("**Indexed files:**")
        for fname in st.session_state.indexed_files:
            st.markdown(f"- `{fname}`")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='color:#8b949e;font-size:12px;'>"
        "<b>Tips:</b><br>"
        "• Upload files for code-aware answers<br>"
        "• Python blocks have a ▶ Run button<br>"
        "• Switch Task Mode to change behaviour"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='display:flex;align-items:center;gap:10px;"
    "padding:10px 0;border-bottom:1px solid #30363d;margin-bottom:16px;'>"
    "<span style='font-size:22px;'>💻</span>"
    "<span style='font-size:18px;font-weight:700;color:#e6edf3;'>AI Coding Assistant</span>"
    "<span style='margin-left:auto;font-size:12px;color:#8b949e;'>GitHub Copilot-style · LangChain</span>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Chat History ───────────────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

        # Run buttons for Python blocks in previous AI messages
        if msg["role"] == "assistant":
            blocks = extract_python_blocks(msg["content"])
            for j, code in enumerate(blocks):
                if st.button("▶ Run Python", key=f"run_{i}_{j}"):
                    with st.expander("📤 Output", expanded=True):
                        st.code(execute_python(code), language="text")

# ── Input & Response ───────────────────────────────────────────────────────────
placeholder = f"Ask me to {selected_task.split()[-1].lower()} code"
if selected_language != "Auto-detect":
    placeholder += f"  [{selected_language}]"
placeholder += "…"

user_input = st.chat_input(placeholder)

if user_input and user_input.strip():
    # Prepend language hint
    full_input = user_input
    if selected_language != "Auto-detect":
        full_input = f"[Target language: {selected_language}]\n\n{user_input}"

    # Build system prompt (task + RAG)
    system_prompt = TASK_PROMPTS[selected_task] + get_rag_context(user_input)

    # Persist user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Stream AI response
    with st.chat_message("assistant", avatar="🤖"):
        try:
            llm   = get_llm(selected_model)
            chain = build_chain(llm, system_prompt)
            response = st.write_stream(
                chain.stream({"input": full_input, "chat_history": get_history()})
            )
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Inline run buttons for freshly generated Python
            blocks = extract_python_blocks(response)
            for j, code in enumerate(blocks):
                if st.button("▶ Run Python", key=f"run_new_{j}"):
                    with st.expander("📤 Output", expanded=True):
                        st.code(execute_python(code), language="text")

        except Exception as e:
            st.error(f"Error: {e}")
