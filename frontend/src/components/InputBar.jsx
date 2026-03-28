import { useRef, useState } from 'react'

export default function InputBar({ onSubmit, disabled, task, language }) {
  const [value, setValue] = useState('')
  const ref = useRef(null)

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setValue('')
    if (ref.current) {
      ref.current.style.height = 'auto'
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const handleInput = (e) => {
    setValue(e.target.value)
    // auto-resize
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 180) + 'px'
  }

  const taskLabel = {
    write: 'Write Code', debug: 'Debug', explain: 'Explain',
    optimize: 'Optimize', review: 'Review',
  }[task] || 'Ask'

  const langHint = language !== 'Auto-detect' ? ` · ${language}` : ''

  return (
    <div className="input-bar-wrap">
      <div className="input-bar">
        <textarea
          ref={ref}
          rows={1}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKey}
          placeholder={`${taskLabel}${langHint}… (Enter to send, Shift+Enter for newline)`}
          disabled={disabled}
        />
        <button className="send-btn" onClick={submit} disabled={disabled || !value.trim()} title="Send (Enter)">
          {disabled ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" strokeDasharray="30" strokeDashoffset="10">
                <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
              </circle>
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          )}
        </button>
      </div>
      <div className="input-hint">AI can make mistakes. Always review generated code.</div>
    </div>
  )
}
