import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { MainLayout } from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Messages from './pages/Messages'
import Settings from './pages/Settings'
import Logs from './pages/Logs'
import Login from './pages/Login'
import TestAgent from './pages/TestAgent'
import { useAuthStore } from './services/auth'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="messages" element={<Messages />} />
        <Route path="test-agent" element={<TestAgent />} />
        <Route path="logs" element={<Logs />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
