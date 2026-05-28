import clsx from 'clsx'

const statusConfig = {
  received:        { label: 'Recebida',      cls: 'badge-blue'   },
  processing:      { label: 'Processando',   cls: 'badge-yellow' },
  responded:       { label: 'Respondida',    cls: 'badge-green'  },
  pending_approval:{ label: 'Aguard. Aprova',cls: 'badge-yellow' },
  approved:        { label: 'Aprovada',      cls: 'badge-green'  },
  rejected:        { label: 'Rejeitada',     cls: 'badge-red'    },
  error:           { label: 'Erro',          cls: 'badge-red'    },
  ignored:         { label: 'Ignorada',      cls: 'badge-gray'   },
}

export function StatusBadge({ status }) {
  const cfg = statusConfig[status] || { label: status, cls: 'badge-gray' }
  return <span className={cfg.cls}>{cfg.label}</span>
}

export function LogLevelBadge({ level }) {
  const cfg = {
    debug:    'badge-gray',
    info:     'badge-blue',
    warning:  'badge-yellow',
    error:    'badge-red',
    critical: 'badge-red',
  }
  return <span className={clsx(cfg[level] || 'badge-gray', 'uppercase text-[10px] tracking-wider')}>{level}</span>
}

export function AiBadge({ enabled }) {
  return enabled
    ? <span className="badge badge-green"><span className="pulse-dot bg-emerald-500" />IA Ativa</span>
    : <span className="badge badge-gray"><span className="pulse-dot bg-slate-400" />IA Inativa</span>
}

export function BusinessHoursBadge({ isBusinessHours }) {
  return isBusinessHours
    ? <span className="badge badge-blue">🕐 Horário Comercial</span>
    : <span className="badge badge-purple">🌙 Fora do Horário</span>
}
