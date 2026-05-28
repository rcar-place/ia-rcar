import { useState, useCallback, useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useWebSocket } from '../websocket/useWebSocket'
import { useQueryClient } from '@tanstack/react-query'
import { Menu, X } from 'lucide-react'

export function MainLayout() {
  const queryClient = useQueryClient()
  const [notifications, setNotifications] = useState([])
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  // Fechar menu ao mudar de rota
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [location])

  const handleWsMessage = useCallback((event) => {
    if (['message_received', 'response_sent', 'pending_approval'].includes(event.type)) {
      queryClient.invalidateQueries({ queryKey: ['messages'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    }
    if (event.type === 'response_sent' || event.type === 'message_received') {
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    }

    const label = {
      message_received:    '📨 Nova mensagem recebida',
      response_sent:       '✅ Resposta enviada',
      pending_approval:    '⏳ Aprovação pendente',
      manual_review_required: '⚠️ Revisão manual necessária',
    }[event.type]

    if (label) {
      const id = Date.now()
      setNotifications((prev) => [...prev.slice(-4), { id, label }])
      setTimeout(() => setNotifications((prev) => prev.filter((n) => n.id !== id)), 4000)
    }
  }, [queryClient])

  const { connected } = useWebSocket(handleWsMessage)

  return (
    <div className="flex min-h-screen relative bg-slate-50">
      {/* Decorative Blur Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-400/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-400/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 z-40 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-blue-500 flex items-center justify-center">
            <span className="text-white font-bold font-display">ML</span>
          </div>
          <span className="font-display font-bold text-slate-900 tracking-wide">AutoResponder</span>
        </div>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-slate-600">
          {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      <div className="p-4 md:p-6 flex w-full gap-6 z-10 relative mt-16 md:mt-0">
        <Sidebar wsConnected={connected} isMobileOpen={isMobileMenuOpen} />
        
        <main className="flex-1 overflow-auto rounded-2xl bg-white/60 backdrop-blur-sm border border-slate-200 shadow-lg relative min-h-[calc(100vh-8rem)] md:min-h-0">
          <Outlet />
        </main>
      </div>

      {/* Overlay mobile */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Toast Notifications */}
      <div className="fixed bottom-5 right-5 flex flex-col gap-2 z-50">
        {notifications.map((n) => (
          <div
            key={n.id}
            className="bg-white border border-slate-200 text-sm text-slate-800
                       px-4 py-3 rounded-xl shadow-xl animate-slide-in"
          >
            {n.label}
          </div>
        ))}
      </div>
    </div>
  )
}
