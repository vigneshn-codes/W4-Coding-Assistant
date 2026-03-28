# 💻 AI Coding Assistant

A GitHub Copilot-style coding assistant built with **React + FastAPI + LangChain**. Supports OpenAI and local Ollama models with real-time streaming, RAG context from uploaded files, and sandboxed code execution.

---

## 🚀 Features

| Feature | Details |
|---|---|
| **GitHub Copilot UI** | VS Code dark theme, chat interface, syntax-highlighted code blocks |
| **Streaming responses** | Real-time token-by-token output via Server-Sent Events |
| **Multi-model support** | OpenAI (GPT-4o, GPT-4o Mini) + local Ollama (Llama 3.2, Llama 3.1, CodeLlama) |
| **Task modes** | Write Code, Debug, Explain, Optimize, Review — each with a specialized prompt |
| **Language selector** | 12 languages injected into the prompt context |
| **Conversation memory** | Full chat history passed on every request |
| **RAG file context** | Upload code/docs → chunked → FAISS vector store → auto-retrieved per query |
| **Code execution** | Run Python blocks inline with a sandboxed subprocess (10s timeout) |
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
        └── Subprocess executor  ←  Python code runner
```

---

## 📦 Tech Stack

**Backend**
- Python 3.12
- FastAPI + Uvicorn
- LangChain (`langchain-openai`, `langchain-ollama`, `langchain-community`)
- FAISS (vector store for RAG)

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

Create a `.env` file in the project root:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

> Ollama models run locally and do **not** require an API key.

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

## 🦙 Using Ollama (local models)

1. Install Ollama: https://ollama.com
2. Pull a model:
```bash
ollama pull llama3.2
```
3. Make sure Ollama is running (`ollama serve`)
4. Select `🦙 Llama 3.2 (local)` from the model dropdown in the UI

---

## 🗂️ Project Structure

```
W4-Coding-Assistant/
├── backend/
│   ├── main.py          # FastAPI app — chat, upload, execute endpoints
│   ├── app.py           # Legacy Streamlit version
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Root component, streaming logic
│   │   ├── index.css             # GitHub Copilot dark theme
│   │   └── components/
│   │       ├── Sidebar.jsx       # Model, task, language, file upload
│   │       ├── ChatWindow.jsx    # Message list + empty state
│   │       ├── Message.jsx       # Markdown renderer with code blocks
│   │       ├── CodeBlock.jsx     # Syntax highlight + copy + run
│   │       └── InputBar.jsx      # Auto-resize textarea, send button
│   ├── package.json
│   └── vite.config.js   # Dev proxy: /api → localhost:8000
├── Readme.md
└── .env                 # OPENAI_API_KEY (not committed)
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
