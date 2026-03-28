import { useRef } from 'react'

const MODELS = [
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini  (fast)' },
  { value: 'gpt-4o',      label: 'GPT-4o  (powerful)' },
  { value: 'llama3.2',    label: '🦙 Llama 3.2  (local)' },
  { value: 'llama3.1',    label: '🦙 Llama 3.1  (local)' },
  { value: 'codellama',   label: '🦙 CodeLlama  (local)' },
]

const LANGUAGES = [
  'Auto-detect','Python','JavaScript','TypeScript',
  'Go','Rust','Java','C++','C#','Ruby','PHP','Swift','Kotlin',
]

const TASKS = [
  { value: 'write',    label: '✏️ Write' },
  { value: 'debug',    label: '🐛 Debug' },
  { value: 'explain',  label: '📖 Explain' },
  { value: 'optimize', label: '⚡ Optimize' },
  { value: 'review',   label: '🔍 Review' },
]

export default function Sidebar({
  model, setModel,
  language, setLanguage,
  task, setTask,
  indexedFiles, onFileUpload, onClearChat,
}) {
  const fileRef = useRef(null)

  const handleFiles = async (e) => {
    const files = Array.from(e.target.files)
    for (const file of files) {
      const form = new FormData()
      form.append('file', file)
      await fetch('/api/upload', { method: 'POST', body: form })
      onFileUpload(file.name)
    }
    e.target.value = ''
  }

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
        </svg>
        <div className="sidebar-logo-text">
          AI Coding Assistant
          <span>GitHub Copilot-style</span>
        </div>
      </div>

      {/* Model */}
      <div className="sidebar-section">
        <div className="sidebar-label">Model</div>
        <select value={model} onChange={e => setModel(e.target.value)}>
          {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
        </select>
      </div>

      {/* Task */}
      <div className="sidebar-section">
        <div className="sidebar-label">Task Mode</div>
        <div className="task-grid">
          {TASKS.map(t => (
            <button
              key={t.value}
              className={`task-btn ${task === t.value ? 'active' : ''}`}
              onClick={() => setTask(t.value)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Language */}
      <div className="sidebar-section">
        <div className="sidebar-label">Language</div>
        <select value={language} onChange={e => setLanguage(e.target.value)}>
          {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>

      {/* File Upload / RAG */}
      <div className="sidebar-section">
        <div className="sidebar-label">Context Files (RAG)</div>
        <div className="upload-area" onClick={() => fileRef.current?.click()}>
          <input
            ref={fileRef}
            type="file"
            multiple
            accept=".py,.js,.ts,.go,.java,.cpp,.c,.cs,.md,.txt,.json"
            onChange={handleFiles}
            style={{ display: 'none' }}
          />
          <div className="upload-icon">📎</div>
          <div>Click to upload code or docs</div>
          <div style={{ fontSize: '10px', marginTop: 2, color: '#6e7681' }}>py, js, ts, go, java, md, txt…</div>
        </div>

        {indexedFiles.length > 0 && (
          <div className="indexed-files">
            {indexedFiles.map(f => (
              <div key={f} className="indexed-file">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                {f}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <button className="clear-btn" onClick={onClearChat}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
          </svg>
          Clear Chat
        </button>
      </div>
    </aside>
  )
}
