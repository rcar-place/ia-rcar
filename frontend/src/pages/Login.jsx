import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../services/auth'
import { Zap, Loader2, Eye, EyeOff } from 'lucide-react'

export default function Login() {
  const { login } = useAuthStore()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.username, form.password)
      navigate('/')
    } catch {
      setError('Usuário ou senha inválidos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      {/* Gradient bg */}
      <div className="absolute inset-0 bg-gradient-to-br from-brand-500/10 via-slate-50 to-blue-500/10 pointer-events-none" />

      <div className="relative w-full max-w-sm space-y-6">
        {/* Logo */}
        <div className="text-center">
          <div className="w-14 h-14 rounded-2xl bg-brand-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-brand-500/25">
            <Zap className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">ML AutoResponder</h1>
          <p className="text-sm text-slate-500 mt-1">Painel de controle administrativo</p>
        </div>

        {/* Form */}
        <div className="card border-slate-200 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-slate-500 block mb-1.5">Usuário</label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                required
                value={form.username}
                onChange={(e) => setForm(f => ({ ...f, username: e.target.value }))}
                className="input"
                placeholder="admin"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 block mb-1.5">Senha</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPass ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={form.password}
                  onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))}
                  className="input pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(s => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
                {error}
              </p>
            )}

            <button
              id="login-btn"
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Entrar
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-slate-500">
          Sistema interno — acesso restrito
        </p>
      </div>
    </div>
  )
}
