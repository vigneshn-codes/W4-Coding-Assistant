import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import InputBar from './components/InputBar'

export default function App() {
  const [messages,     setMessages]     = useState([])
  const [model,        setModel]        = useState('gpt-4o-mini')
  const [language,     setLanguage]     = useState('Auto-detect')
  const [task,         setTask]         = useState('write')
  const [indexedFiles, setIndexedFiles] = useState([])
  const [loading,      setLoading]      = useState(false)

  const handleSend = async (input) => {
    if (loading) return

    // Add user message
    const userMsg = { role: 'user', content: input }
    const history = [...messages, userMsg]
    setMessages([...history, { role: 'assistant', content: '' }])
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input,
          model,
          language,
          task,
          // pass history without the empty placeholder we just added
          history: messages.map(m => ({ role: m.role, content: m.content })),
        }),
      })

      if (!res.ok) throw new Error(`Server error: ${res.status}`)

      const reader  = res.body.getReader()
      const decoder = new TextDecoder()
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text  = decoder.decode(value, { stream: true })
        const lines = text.split('\n')

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const payload = line.slice(6).trim()
          if (payload === '[DONE]') break
          try {
            const { token, error } = JSON.parse(payload)
            if (error) throw new Error(error)
            accumulated += token
            setMessages(prev => {
              const copy = [...prev]
              copy[copy.length - 1] = { role: 'assistant', content: accumulated }
              return copy
            })
          } catch {}
        }
      }
    } catch (err) {
      setMessages(prev => {
        const copy = [...prev]
        copy[copy.length - 1] = {
          role: 'assistant',
          content: `❌ **Error:** ${err.message}`,
        }
        return copy
      })
    }

    setLoading(false)
  }

  const handleClearChat = () => setMessages([])

  const handleFileUpload = (filename) => {
    setIndexedFiles(prev => prev.includes(filename) ? prev : [...prev, filename])
  }

  const taskLabel = {
    write: 'Write', debug: 'Debug', explain: 'Explain',
    optimize: 'Optimize', review: 'Review',
  }[task]

  return (
    <div className="app">
      <Sidebar
        model={model}           setModel={setModel}
        language={language}     setLanguage={setLanguage}
        task={task}             setTask={setTask}
        indexedFiles={indexedFiles}
        onFileUpload={handleFileUpload}
        onClearChat={handleClearChat}
      />

      <div className="main">
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-left">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#58a6ff" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            Copilot Chat
            <span className="chat-header-badge">{taskLabel}</span>
            {language !== 'Auto-detect' && (
              <span className="chat-header-badge" style={{ borderColor: '#2ea043', color: '#4ec9b0', background: '#0d2818' }}>
                {language}
              </span>
            )}
          </div>
          <div className="chat-header-meta">
            {messages.length > 0 ? `${messages.filter(m => m.role === 'user').length} message${messages.filter(m => m.role === 'user').length !== 1 ? 's' : ''}` : 'No messages yet'}
          </div>
        </div>

        <ChatWindow messages={messages} onSuggestion={handleSend} />

        <InputBar
          onSubmit={handleSend}
          disabled={loading}
          task={task}
          language={language}
        />
      </div>
    </div>
  )
}
