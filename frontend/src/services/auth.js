import { create } from 'zustand'
import { authApi } from './api'

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),

  login: async (username, password) => {
    const data = await authApi.login(username, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const user = await authApi.me()
    set({ user, isAuthenticated: true })
    return user
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
    window.location.href = '/login'
  },

  loadUser: async () => {
    try {
      const user = await authApi.me()
      set({ user, isAuthenticated: true })
    } catch {
      set({ user: null, isAuthenticated: false })
    }
  },
}))
