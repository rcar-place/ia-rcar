import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { LogLevelBadge } from './Badge'

export function LogItem({ log }) {
  const timeAgo = formatDistanceToNow(new Date(log.created_at), {
    addSuffix: true,
    locale: ptBR,
  })

  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-slate-100 last:border-0 animate-fade-in">
      <LogLevelBadge level={log.level} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-700 truncate">{log.message}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-slate-400 font-mono">{log.event}</span>
          {log.message_id && (
            <span className="text-xs text-slate-400">· msg #{log.message_id}</span>
          )}
        </div>
      </div>
      <span className="text-xs text-slate-400 whitespace-nowrap">{timeAgo}</span>
    </div>
  )
}
