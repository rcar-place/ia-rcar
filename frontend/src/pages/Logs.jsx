import { useState } from 'react'
import { ScrollText, RefreshCw } from 'lucide-react'
import { useLogs } from '../hooks/useLogs'
import { LogItem } from '../components/LogItem'
import { useQueryClient } from '@tanstack/react-query'

const LEVEL_OPTIONS = ['', 'debug', 'info', 'warning', 'error', 'critical']

export default function Logs() {
  const [page, setPage] = useState(1)
  const [level, setLevel] = useState('')
  const queryClient = useQueryClient()

  const { data, isLoading, isFetching } = useLogs({
    page,
    per_page: 50,
    ...(level ? { level } : {}),
  })

  const totalPages = data ? Math.ceil(data.total / 50) : 1

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ScrollText className="w-6 h-6 text-brand-500" />
            Logs do Sistema
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data?.total ?? 0} eventos registrados
          </p>
        </div>
        <button
          className="btn-secondary flex items-center gap-2 text-sm"
          onClick={() => queryClient.invalidateQueries({ queryKey: ['logs'] })}
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          Atualizar
        </button>
      </div>

      {/* Filtro de nível */}
      <div className="flex gap-2 flex-wrap">
        {LEVEL_OPTIONS.map((lvl) => (
          <button
            key={lvl || 'all'}
            onClick={() => { setLevel(lvl); setPage(1) }}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              level === lvl
                ? 'bg-brand-50 border-brand-200 text-brand-700'
                : 'border-slate-200 text-slate-500 hover:text-slate-900 hover:border-slate-300 hover:bg-slate-50'
            }`}
          >
            {lvl || 'Todos'}
          </button>
        ))}
      </div>

      {/* Logs */}
      <div className="card">
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-8 bg-slate-100 rounded animate-pulse" />
            ))}
          </div>
        ) : data?.items?.length ? (
          <div>
            {data.items.map((log) => <LogItem key={log.id} log={log} />)}
          </div>
        ) : (
          <p className="text-sm text-slate-500 text-center py-8">Nenhum log encontrado.</p>
        )}
      </div>

      {/* Paginação */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            className="btn-secondary text-sm px-3 py-1.5"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >← Anterior</button>
          <span className="text-sm text-slate-500">Página {page} de {totalPages}</span>
          <button
            className="btn-secondary text-sm px-3 py-1.5"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >Próxima →</button>
        </div>
      )}
    </div>
  )
}
