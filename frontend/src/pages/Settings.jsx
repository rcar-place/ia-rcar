import { useState } from 'react'
import { Save, Loader2, AlertCircle, CheckCircle2, Clock, Bot, Shield, List } from 'lucide-react'
import { useSettings, useUpdateSettings } from '../hooks/useSettings'

function Toggle({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative w-11 h-6 rounded-full transition-colors duration-200 focus:outline-none
        ${checked ? 'bg-brand-500' : 'bg-slate-200'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <span
        className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200
          ${checked ? 'translate-x-5' : 'translate-x-0'}`}
      />
    </button>
  )
}

function Section({ icon: Icon, title, children }) {
  return (
    <div className="card space-y-4">
      <h2 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
        <Icon className="w-4 h-4 text-brand-500" />
        {title}
      </h2>
      {children}
    </div>
  )
}

export default function Settings() {
  const { data, isLoading } = useSettings()
  const { mutate: update, isPending, isSuccess, isError } = useUpdateSettings()
  const [form, setForm] = useState(null)

  // Inicializa o form quando os dados chegam
  if (data && !form) {
    setForm({ ...data })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (form) update(form)
  }

  if (isLoading || !form) {
    return (
      <div className="p-6 flex items-center gap-2 text-slate-500">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Carregando configurações...</span>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Configurações</h1>
        <p className="text-sm text-slate-500 mt-0.5">Controle o comportamento da IA e do sistema</p>
      </div>

      {isSuccess && (
        <div className="flex items-center gap-2 text-emerald-400 text-sm bg-emerald-400/10 border border-emerald-400/20 px-4 py-3 rounded-lg">
          <CheckCircle2 className="w-4 h-4" />
          Configurações salvas com sucesso!
        </div>
      )}
      {isError && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 border border-red-400/20 px-4 py-3 rounded-lg">
          <AlertCircle className="w-4 h-4" />
          Erro ao salvar. Verifique as permissões.
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* IA */}
        <Section icon={Bot} title="Inteligência Artificial">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-800">Resposta automática da IA</p>
              <p className="text-xs text-slate-500 mt-0.5">Quando desativada, nenhuma mensagem é respondida automaticamente</p>
            </div>
            <Toggle
              checked={form.ai_enabled}
              onChange={(v) => setForm(f => ({ ...f, ai_enabled: v }))}
            />
          </div>

          <div>
            <label className="text-xs text-slate-500 block mb-1.5">
              Nível de confiança mínimo ({Math.round(form.ai_confidence_threshold * 100)}%)
            </label>
            <input
              type="range"
              min={0} max={1} step={0.05}
              value={form.ai_confidence_threshold}
              onChange={(e) => setForm(f => ({ ...f, ai_confidence_threshold: parseFloat(e.target.value) }))}
              className="w-full accent-brand-500"
            />
            <div className="flex justify-between text-xs text-slate-600 mt-0.5">
              <span>0% (sempre envia)</span>
              <span>100% (muito rigoroso)</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-800">Aprovação manual obrigatória</p>
              <p className="text-xs text-slate-500 mt-0.5">Todas as respostas precisam de aprovação humana antes do envio</p>
            </div>
            <Toggle
              checked={form.manual_approval_required}
              onChange={(v) => setForm(f => ({ ...f, manual_approval_required: v }))}
            />
          </div>
        </Section>

        {/* Horário */}
        <Section icon={Clock} title="Horário Comercial">
          <p className="text-xs text-slate-500">
            A IA responde <strong className="text-slate-800">somente fora</strong> deste período.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-500 block mb-1.5">Início (hora)</label>
              <input
                type="number" min={0} max={23}
                value={form.business_hour_start}
                onChange={(e) => setForm(f => ({ ...f, business_hour_start: parseInt(e.target.value) }))}
                className="input"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 block mb-1.5">Fim (hora)</label>
              <input
                type="number" min={0} max={23}
                value={form.business_hour_end}
                onChange={(e) => setForm(f => ({ ...f, business_hour_end: parseInt(e.target.value) }))}
                className="input"
              />
            </div>
          </div>
          <p className="text-xs text-slate-600">
            Horário atual: segunda a sexta, {form.business_hour_start}h às {form.business_hour_end}h (Brasília)
          </p>
        </Section>

        {/* Blacklist */}
        <Section icon={Shield} title="Blacklist de Palavras">
          <p className="text-xs text-slate-500">
            Mensagens com essas palavras não serão respondidas automaticamente (separadas por vírgula).
          </p>
          <textarea
            rows={3}
            value={form.blacklist_words}
            onChange={(e) => setForm(f => ({ ...f, blacklist_words: e.target.value }))}
            placeholder="reembolso, cancelar, processo, advogado..."
            className="input resize-none"
          />
        </Section>

        {/* Resposta */}
        <Section icon={List} title="Resposta">
          <div>
            <label className="text-xs text-slate-500 block mb-1.5">
              Comprimento máximo da resposta ({form.max_response_length} caracteres)
            </label>
            <input
              type="range" min={50} max={2000} step={50}
              value={form.max_response_length}
              onChange={(e) => setForm(f => ({ ...f, max_response_length: parseInt(e.target.value) }))}
              className="w-full accent-brand-500"
            />
          </div>
        </Section>

        <button type="submit" disabled={isPending} className="btn-primary flex items-center gap-2">
          {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Salvar Configurações
        </button>
      </form>
    </div>
  )
}
