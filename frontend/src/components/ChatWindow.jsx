import { useEffect, useRef } from 'react'
import Message from './Message'

const SUGGESTIONS = [
  { label: 'Write Code',  text: 'Write a Python FastAPI endpoint with JWT auth' },
  { label: 'Debug',       text: 'Find and fix bugs in my code' },
  { label: 'Explain',     text: 'Explain how async/await works in JavaScript' },
  { label: 'Optimize',    text: 'Optimize this database query for performance' },
]

export default function ChatWindow({ messages, onSuggestion }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="chat-window">
        <div className="chat-empty">
          <div className="chat-empty-icon">💻</div>
          <h2>AI Coding Assistant</h2>
          <p>Your GitHub Copilot-style assistant. Ask anything about writing, debugging, explaining, or reviewing code.</p>
          <div className="suggestion-grid">
            {SUGGESTIONS.map((s, i) => (
              <button key={i} className="suggestion-card" onClick={() => onSuggestion(s.text)}>
                <div className="suggestion-card-label">{s.label}</div>
                <div className="suggestion-card-text">{s.text}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-window">
      {messages.map((msg, i) => (
        <Message key={i} msg={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
