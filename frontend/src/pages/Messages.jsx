import { useState } from 'react'
import { Filter, RefreshCw } from 'lucide-react'
import { useMessages, useApproveMessage } from '../hooks/useMessages'
import { MessageCard } from '../components/MessageCard'
import { useQueryClient } from '@tanstack/react-query'

const STATUS_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'received', label: 'Recebidas' },
  { value: 'processing', label: 'Processando' },
  { value: 'responded', label: 'Respondidas' },
  { value: 'pending_approval', label: 'Aguard. Aprovação' },
  { value: 'ignored', label: 'Ignoradas' },
  { value: 'error', label: 'Erros' },
]

export default function Messages() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')
  const queryClient = useQueryClient()

  const { data, isLoading, isFetching } = useMessages({
    page,
    per_page: 15,
    ...(status ? { status } : {}),
  })

  const totalPages = data ? Math.ceil(data.total / 15) : 1

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mensagens</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data?.total ?? 0} mensagens encontradas
          </p>
        </div>
        <button
          className="btn-secondary flex items-center gap-2 text-sm"
          onClick={() => queryClient.invalidateQueries({ queryKey: ['messages'] })}
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          Atualizar
        </button>
      </div>

      {/* Filtros */}
      <div className="flex items-center gap-3 flex-wrap">
        <Filter className="w-4 h-4 text-slate-500" />
        {STATUS_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setStatus(opt.value); setPage(1) }}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              status === opt.value
                ? 'bg-brand-50 border-brand-200 text-brand-700'
                : 'border-slate-200 text-slate-500 hover:text-slate-900 hover:border-slate-300 hover:bg-slate-50'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Lista */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card h-24 animate-pulse bg-slate-100" />
          ))}
        </div>
      ) : data?.items?.length ? (
        <div className="space-y-3">
          {data.items.map((msg) => (
            <MessageCard key={msg.id} message={msg} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-slate-500">Nenhuma mensagem encontrada.</p>
        </div>
      )}

      {/* Paginação */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            className="btn-secondary text-sm px-3 py-1.5"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            ← Anterior
          </button>
          <span className="text-sm text-slate-500">
            Página {page} de {totalPages}
          </span>
          <button
            className="btn-secondary text-sm px-3 py-1.5"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  )
}
