import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  Settings,
  ScrollText,
  LogOut,
  Zap,
  Wifi,
  WifiOff,
  Bot
} from 'lucide-react'
import { useAuthStore } from '../services/auth'
import clsx from 'clsx'

const NAV = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard'  },
  { to: '/messages',  icon: MessageSquare,   label: 'Mensagens'  },
  { to: '/test-agent',icon: Bot,             label: 'Testar IA'  },
  { to: '/logs',      icon: ScrollText,      label: 'Logs'       },
  { to: '/settings',  icon: Settings,        label: 'Configurações' },
]

export function Sidebar({ wsConnected, isMobileOpen }) {
  const { user, logout } = useAuthStore()

  return (
    <aside className={clsx(
      "w-64 shrink-0 rounded-2xl bg-white/90 backdrop-blur-xl border border-slate-200 flex flex-col shadow-lg relative overflow-hidden transition-all duration-300 z-50",
      "fixed md:relative top-16 md:top-0 bottom-4 md:bottom-0 left-4 md:left-0",
      isMobileOpen ? "translate-x-0" : "-translate-x-[150%] md:translate-x-0"
    )}>
      {/* Logo */}
      <div className="px-5 py-6 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-blue-500 flex items-center justify-center shadow-md shadow-brand-500/20">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900 font-display tracking-wide">ML AutoResponder</p>
            <p className="text-[10px] text-brand-600 font-semibold uppercase tracking-widest mt-0.5">IA · Painel</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx('sidebar-link', isActive && 'active')
            }
          >
            <Icon className="w-4 h-4" />
            <span className="font-medium tracking-wide">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-100 space-y-3">
        {/* WebSocket status */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 text-xs font-medium">
          {wsConnected ? (
            <>
              <div className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </div>
              <span className="text-emerald-400">Tempo real ativo</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-slate-500">Reconectando...</span>
            </>
          )}
        </div>

        {/* User */}
        <div className="flex items-center justify-between px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-100">
          <div>
            <p className="text-sm font-semibold text-slate-800">{user?.username || '—'}</p>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-0.5">{user?.is_admin ? 'Admin' : 'Usuário'}</p>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors"
            title="Sair"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
