import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import CodeBlock from './CodeBlock'

export default function Message({ msg }) {
  const isUser = msg.role === 'user'

  return (
    <div className={`message ${msg.role}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-body">
        <div className="message-role">{isUser ? 'You' : 'Copilot'}</div>
        <div className="message-content">
          {msg.content === '' && !isUser ? (
            <div className="typing-dots">
              <span /><span /><span />
            </div>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '')
                  const code  = String(children).replace(/\n$/, '')
                  if (!inline && match) {
                    return <CodeBlock language={match[1]} code={code} />
                  }
                  return <code className={className} {...props}>{children}</code>
                },
                // open links in new tab
                a({ href, children }) {
                  return <a href={href} target="_blank" rel="noreferrer">{children}</a>
                },
              }}
            >
              {msg.content}
            </ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  )
}
