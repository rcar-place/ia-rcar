import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { MessageCircle, Bot, Clock, User } from 'lucide-react'
import { StatusBadge } from './Badge'
import { useNavigate } from 'react-router-dom'

export function MessageCard({ message, compact = false }) {
  const navigate = useNavigate()
  const timeAgo = formatDistanceToNow(new Date(message.created_at), {
    addSuffix: true,
    locale: ptBR,
  })

  return (
    <div
      className="card hover:border-brand-300 cursor-pointer transition-all duration-200 animate-fade-in"
      onClick={() => navigate(`/messages/${message.id}`)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center">
            <User className="w-4 h-4 text-brand-600" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-800 truncate">
              {message.ml_buyer_nickname || message.ml_buyer_id}
            </p>
            <p className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" /> {timeAgo}
            </p>
          </div>
        </div>
        <StatusBadge status={message.status} />
      </div>

      <p className="mt-3 text-sm text-slate-600 line-clamp-2">
        {message.text_sanitized}
      </p>

      {!compact && message.response && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <div className="flex items-start gap-2">
            <Bot className="w-4 h-4 text-brand-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-slate-600 line-clamp-2 italic">
              {message.response.text}
            </p>
          </div>
          {message.response.confidence_score > 0 && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-slate-400">Confiança IA</span>
              <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-brand-500 rounded-full transition-all"
                  style={{ width: `${message.response.confidence_score * 100}%` }}
                />
              </div>
              <span className="text-xs text-slate-500">
                {(message.response.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
