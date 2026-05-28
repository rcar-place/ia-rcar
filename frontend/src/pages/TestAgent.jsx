import { useState, useRef, useEffect } from 'react'
import { Bot, Send, User, AlertCircle } from 'lucide-react'
import { api } from '../services/api'

export default function TestAgent() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Olá! Sou a Inteligência Artificial configurada para o Mercado Livre. Envie uma mensagem de teste para ver como eu responderia a um comprador real.' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Comentado para evitar que a tela role para baixo automaticamente
  // useEffect(() => {
  //   if (messages.length > 1) {
  //     scrollToBottom()
  //   }
  // }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await api.post('/messages/test-ai', { message: userMessage })
      setMessages((prev) => [...prev, { role: 'assistant', content: response.data.response }])
    } catch (error) {
      setMessages((prev) => [...prev, { 
        role: 'system', 
        content: `Erro ao comunicar com a IA: ${error.message}` 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col p-4 md:p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold font-display bg-clip-text text-transparent bg-gradient-to-r from-brand-500 to-blue-600 tracking-tight">Testar IA (Sandbox)</h1>
        <p className="text-sm text-slate-500 mt-1 font-medium">Simule conversas de clientes sem afetar o Mercado Livre real.</p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 bg-white/80 backdrop-blur-xl border border-slate-200 rounded-2xl flex flex-col shadow-lg overflow-hidden relative">
        {/* Decorative background */}
        <div className="absolute inset-0 bg-gradient-to-b from-brand-400/5 to-transparent pointer-events-none" />

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 z-10">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div className={`w-8 h-8 md:w-10 md:h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                msg.role === 'user' ? 'bg-slate-100 text-slate-600' :
                msg.role === 'assistant' ? 'bg-gradient-to-br from-brand-400 to-blue-500 text-white' :
                'bg-red-100 text-red-600'
              }`}>
                {msg.role === 'user' ? <User className="w-5 h-5" /> : 
                 msg.role === 'assistant' ? <Bot className="w-5 h-5" /> : 
                 <AlertCircle className="w-5 h-5" />}
              </div>

              <div className={`max-w-[85%] md:max-w-[70%] px-4 py-3 rounded-2xl text-sm shadow-sm ${
                msg.role === 'user' ? 'bg-slate-100 text-slate-800 rounded-tr-none' :
                msg.role === 'assistant' ? 'bg-white text-slate-800 border border-slate-200 rounded-tl-none' :
                'bg-red-50 border border-red-200 text-red-700 rounded-tl-none'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-xl bg-gradient-to-br from-brand-400 to-blue-500 text-white flex items-center justify-center shrink-0 shadow-sm animate-pulse">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none border border-slate-200 flex items-center gap-1.5 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-slate-200 bg-slate-50/50 z-10">
          <form onSubmit={handleSend} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite uma mensagem do comprador..."
              className="w-full bg-white border border-slate-300 rounded-xl pl-4 pr-12 py-3.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all shadow-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2 bg-brand-500 hover:bg-brand-400 text-slate-900 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
