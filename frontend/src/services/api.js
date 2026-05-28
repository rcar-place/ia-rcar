import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Injeta token JWT em todas as requisições
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Trata expiração de token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          return api.request(error.config)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      } else {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── API helpers ────────────────────────────────────────────────────────────

export const authApi = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }).then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
}

export const messagesApi = {
  list: (params) => api.get('/messages/', { params }).then((r) => r.data),
  get: (id) => api.get(`/messages/${id}`).then((r) => r.data),
  dashboard: () => api.get('/messages/dashboard').then((r) => r.data),
  approve: (id, approved, reason) =>
    api.post(`/messages/${id}/approve`, { approved, reason }).then((r) => r.data),
}

export const settingsApi = {
  get: () => api.get('/settings/').then((r) => r.data),
  update: (data) => api.put('/settings/', data).then((r) => r.data),
}

export const logsApi = {
  list: (params) => api.get('/logs/', { params }).then((r) => r.data),
}
