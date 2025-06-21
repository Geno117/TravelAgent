import { useState, useRef } from 'react'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const chatWindowRef = useRef<HTMLDivElement>(null)

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!input.trim()) return
    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    let assistantMessage: Message = { role: 'assistant', content: '' }
    setMessages((prev) => [...prev, assistantMessage])

    try {
      const response = await fetch('http://localhost:5001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content }),
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: data.response }
        return updated
      })
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: 'Error: Could not get response.' }
        return updated
      })
    } finally {
      setIsLoading(false)
      setTimeout(() => {
        chatWindowRef.current?.scrollTo({ top: chatWindowRef.current.scrollHeight, behavior: 'smooth' })
      }, 100)
    }
  }

  return (
    <div className="app-container">
      <h1>Travel Agent Chat</h1>
      <div className="chat-window" ref={chatWindowRef}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <b>{msg.role === 'user' ? 'You' : 'Agent'}:</b> {msg.content}
          </div>
        ))}
        {isLoading && <div className="chat-message assistant">Agent is typing...</div>}
      </div>
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your query..."
          className="input-box"
          disabled={isLoading}
        />
        <button type="submit" className="submit-button" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

export default App
