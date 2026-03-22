# 💻 AI Coding Assistant (LangChain + Streamlit)

A simple AI-powered coding assistant built using:
- Python
- Streamlit
- LangChain (latest version, no deprecated APIs)
- OpenAI API

---

## 🚀 Features

- Ask coding questions
- Get clean and optimized code
- Explanation + improvements
- Uses latest LangChain runnable chains (no deprecated LLMChain)

---

## 🧠 Architecture

User Input → Prompt Template → LLM (OpenAI) → Output Parser → UI

LangChain Flow:

prompt | llm | parser

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd ai-coding-assistant```
### 2. Create Virtual Environment
```bash
ython -m venv venv```
```bash
dsource venv/bin/activate  # Mac/Linux```
```bash
dvenv\Scripts\activate     # Windows```
### 3. Install Dependencies
```bash
pip install -r requirements.txt```
🔐 Setup API Key:
Create a `.env` file:
```plaintext
OPENAI_API_KEY=your_api_key_here```
▶️ Run Application:
```bash
treamlit run app.py```
🧪 Example Queries:
- "Write a Node.js API with Express"
- "Optimize this Python loop"
- "Explain async/await in JavaScript"
- "Fix this bug: <code>"
⚠️ LangChain Deprecation Fix 
``` 
--- 
### 👨‍💻 Author 
Built for learning GenAI + LangChain (latest version)