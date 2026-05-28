import {
  MessageSquare, CheckCircle2, Clock, AlertTriangle,
  Zap, TrendingUp, Activity, Users
} from 'lucide-react'
import { useDashboard } from '../hooks/useMessages'
import { useLogs } from '../hooks/useLogs'
import { AiBadge, BusinessHoursBadge } from '../components/Badge'
import { LogItem } from '../components/LogItem'

function StatCard({ icon: Icon, label, value, color = 'text-brand-400', sub }) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</span>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <p className={`text-3xl font-bold ${color} mt-1`}>{value ?? '—'}</p>
      {sub && <p className="text-xs text-slate-600 mt-0.5">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const { data: stats, isLoading } = useDashboard()
  const { data: logs } = useLogs({ per_page: 10 })

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold font-display bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 tracking-tight">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1 font-medium">Visão geral do sistema em tempo real</p>
        </div>
        <div className="flex items-center gap-3">
          {stats && <BusinessHoursBadge isBusinessHours={stats.is_business_hours} />}
          {stats && <AiBadge enabled={stats.ai_enabled} />}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          icon={MessageSquare}
          label="Total Mensagens"
          value={stats?.total_messages}
          color="text-blue-400"
        />
        <StatCard
          icon={CheckCircle2}
          label="Respondidas"
          value={stats?.responded}
          color="text-emerald-400"
          sub="pela IA automaticamente"
        />
        <StatCard
          icon={Clock}
          label="Pendentes"
          value={stats?.pending}
          color="text-amber-400"
          sub="aguardando processamento"
        />
        <StatCard
          icon={AlertTriangle}
          label="Erros"
          value={stats?.errors}
          color="text-red-400"
        />
      </div>

      {/* Linha 2 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          icon={Zap}
          label="IA Ignorou"
          value={stats?.ignored}
          color="text-slate-400"
          sub="horário comercial"
        />
        <StatCard
          icon={Activity}
          label="WS Conexões"
          value={stats?.ws_connections}
          color="text-purple-400"
          sub="painéis conectados"
        />
        <StatCard
          icon={TrendingUp}
          label="Taxa Resposta"
          value={stats?.total_messages
            ? `${Math.round((stats.responded / stats.total_messages) * 100)}%`
            : '—'
          }
          color="text-brand-400"
        />
      </div>

      {/* Status da IA */}
      <div className="card">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${stats?.ai_enabled ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'}`} />
          <div>
            <p className="text-sm font-semibold text-slate-800">
              {stats?.ai_enabled ? 'Resposta automática ativa' : 'Resposta automática desativada'}
            </p>
            <p className="text-xs text-slate-500">
              {stats?.is_business_hours
                ? 'Dentro do horário comercial — IA aguarda para não interferir com a equipe'
                : 'Fora do horário comercial — IA responde automaticamente'
              }
            </p>
          </div>
        </div>
      </div>

      {/* Logs recentes */}
      <div className="card">
        <h2 className="text-sm font-bold text-slate-800 mb-5 flex items-center gap-2 font-display tracking-wide uppercase">
          <Activity className="w-4 h-4 text-brand-500" />
          Eventos Recentes
        </h2>
        {isLoading ? (
          <p className="text-sm text-slate-600">Carregando...</p>
        ) : logs?.items?.length ? (
          <div>
            {logs.items.map((log) => <LogItem key={log.id} log={log} />)}
          </div>
        ) : (
          <p className="text-sm text-slate-600">Nenhum evento registrado ainda.</p>
        )}
      </div>
    </div>
  )
}
