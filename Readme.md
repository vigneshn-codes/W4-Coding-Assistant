# 💻 AI Coding Assistant

A GitHub Copilot-style coding assistant built with **React + FastAPI + LangChain**. Supports OpenAI and local Ollama models with real-time streaming, RAG context from uploaded files, and sandboxed code execution.

---

## 🚀 Features

| Feature | Details |
|---|---|
| **GitHub Copilot UI** | VS Code dark theme, chat interface, syntax-highlighted code blocks |
| **Streaming responses** | Real-time token-by-token output via Server-Sent Events (SSE) |
| **Multi-model support** | OpenAI (GPT-4o, GPT-4o Mini) + local Ollama (Llama 3.2, DeepSeek, OpenHermes…) |
| **Task modes** | Write Code, Debug, Explain, Optimize, Review — each with a specialized prompt |
| **Language selector** | 12 languages injected into the prompt context |
| **Conversation memory** | Full chat history passed on every request |
| **RAG file context** | Upload code/docs → chunked → FAISS vector store → auto-retrieved per query |
| **Code execution** | Run Python blocks inline with a sandboxed subprocess (10 s timeout) |
| **Copy button** | One-click copy on every code block |

---

## 🧠 Architecture

```
React Frontend (Vite · port 3000)
        │
        │  HTTP / SSE
        ▼
FastAPI Backend (port 8000)
        │
        ├── LangChain Chain
        │     ChatPromptTemplate + MessagesPlaceholder
        │     └── LLM (OpenAI or Ollama)
        │         └── StrOutputParser  →  SSE stream
        │
        ├── FAISS Vector Store  ←  uploaded files (RAG)
        │     └── OpenAI Embeddings (requires OPENAI_API_KEY)
        └── Subprocess executor  ←  Python code runner
```

---

## 📦 Tech Stack

**Backend**
- Python 3.12
- FastAPI + Uvicorn
- LangChain (`langchain-openai`, `langchain-ollama`, `langchain-community`)
- FAISS (vector store for RAG)
- OpenAI Embeddings (used for RAG even with Ollama models)

**Frontend**
- React 18 + Vite
- `react-markdown` + `react-syntax-highlighter` (vscDarkPlus theme)
- `remark-gfm` for GitHub-flavoured markdown

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd W4-Coding-Assistant
```

### 2. Backend setup

```bash
pip install -r backend/requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Environment variables

Create a `.env` file in the **project root**:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

> **Note:** `OPENAI_API_KEY` is required for RAG file indexing (OpenAI Embeddings) even when using local Ollama models for chat. If you don't use file upload, you can skip this for Ollama-only usage.

---

## ▶️ Running the App

**Terminal 1 — Backend**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 🏗️ Production Build

Build the React frontend and serve everything from FastAPI:

```bash
cd frontend
npm run build
```

Then run only the backend — it will automatically serve the built React app:

```bash
uvicorn backend.main:app --port 8000
```

Open `http://localhost:8000`.

---

## 🦙 Using Ollama (local models)

1. Install Ollama: https://ollama.com
2. Pull a model:
```bash
ollama pull llama3.2
```
3. Ensure Ollama is running:
```bash
ollama serve
```
4. Select the model from the dropdown in the UI.

**Models confirmed working locally:**

| Model | Pull command |
|---|---|
| Llama 3.2 (3.2B) | `ollama pull llama3.2` |
| Llama 3.2 Vision (10.7B) | `ollama pull llama3.2-vision` |
| DeepSeek R1 (8B) | `ollama pull deepseek-r1:8b` |
| OpenHermes (7B) | `ollama pull openhermes` |
| CodeLlama | `ollama pull codellama` |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Stream a chat response (SSE) |
| `POST` | `/api/upload` | Upload a file and index it into FAISS |
| `GET` | `/api/files` | List all indexed files |
| `DELETE` | `/api/context` | Clear the RAG vector store |
| `POST` | `/api/execute` | Execute a Python code snippet |

**Chat request body:**
```json
{
  "input": "Write a binary search in Python",
  "model": "llama3.2",
  "language": "Python",
  "task": "write",
  "history": []
}
```

---

## 🗂️ Project Structure

```
W4-Coding-Assistant/
├── backend/
│   ├── main.py          # FastAPI app — chat, upload, execute endpoints
│   ├── app.py           # Legacy Streamlit version
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── vite.config.js   # Dev proxy: /api → localhost:8000
│   ├── package.json
│   └── src/
│       ├── App.jsx               # Root component, streaming logic
│       ├── index.css             # GitHub Copilot dark theme
│       └── components/
│           ├── Sidebar.jsx       # Model, task, language, file upload
│           ├── ChatWindow.jsx    # Message list + empty state
│           ├── Message.jsx       # Markdown renderer with code blocks
│           ├── CodeBlock.jsx     # Syntax highlight + copy + run
│           └── InputBar.jsx      # Auto-resize textarea, send button
├── .env                 # OPENAI_API_KEY (do not commit)
└── Readme.md
```

---

## 🧪 Example Prompts

- *"Write a FastAPI REST API with JWT authentication"*
- *"Debug this Python async function: `<paste code>`"*
- *"Explain how React useEffect works with cleanup"*
- *"Optimize this SQL query for large datasets"*
- *"Review my TypeScript class for best practices"*

---

## 👨‍💻 Author

Built for learning **GenAI + LangChain + React** with a production-style GitHub Copilot experience.
