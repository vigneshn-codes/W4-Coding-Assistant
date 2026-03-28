import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function CodeBlock({ language, code }) {
  const [copied, setCopied] = useState(false)
  const [output, setOutput]   = useState('')
  const [running, setRunning] = useState(false)
  const isPython = ['python', 'py'].includes(language?.toLowerCase())

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleRun = async () => {
    setRunning(true)
    setOutput('')
    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      })
      const data = await res.json()
      setOutput(data.output)
    } catch (e) {
      setOutput(`Error: ${e.message}`)
    }
    setRunning(false)
  }

  return (
    <div className="code-block">
      <div className="code-block-header">
        <span className="code-lang">{language || 'text'}</span>
        <div className="code-actions">
          {isPython && (
            <button className="code-action-btn run" onClick={handleRun} disabled={running}>
              {running ? (
                <>
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" strokeDasharray="30" strokeDashoffset="10">
                      <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
                    </circle>
                  </svg>
                  Running…
                </>
              ) : (
                <>
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  Run
                </>
              )}
            </button>
          )}
          <button className={`code-action-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
            {copied ? (
              <>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Copied
              </>
            ) : (
              <>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                Copy
              </>
            )}
          </button>
        </div>
      </div>

      <SyntaxHighlighter
        language={language || 'text'}
        style={vscDarkPlus}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: '12.5px' }}
        showLineNumbers={code.split('\n').length > 4}
        wrapLongLines={false}
      >
        {code}
      </SyntaxHighlighter>

      {output && (
        <div className="code-output">
          <div className="code-output-label">Output</div>
          <pre>{output}</pre>
        </div>
      )}
    </div>
  )
}
