import { useEffect, useRef, useCallback, useState } from 'react'

const WS_URL = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/updates`
const RECONNECT_DELAY = 3000

/**
 * Hook para conectar ao WebSocket e receber eventos em tempo real.
 * Gerencia reconexão automática.
 */
export function useWebSocket(onMessage) {
  const ws = useRef(null)
  const reconnectTimeout = useRef(null)
  const [connected, setConnected] = useState(false)

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL)

      ws.current.onopen = () => {
        setConnected(true)
        // Inicia ping para manter conexão viva
        const pingInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send('ping')
          }
        }, 30000)
        ws.current._pingInterval = pingInterval
      }

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type !== 'pong') {
            onMessage?.(data)
          }
        } catch {
          // Ignora mensagens malformadas
        }
      }

      ws.current.onclose = () => {
        setConnected(false)
        clearInterval(ws.current?._pingInterval)
        // Reconecta automaticamente
        reconnectTimeout.current = setTimeout(connect, RECONNECT_DELAY)
      }

      ws.current.onerror = () => {
        ws.current?.close()
      }
    } catch {
      reconnectTimeout.current = setTimeout(connect, RECONNECT_DELAY)
    }
  }, [onMessage])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      clearInterval(ws.current?._pingInterval)
      ws.current?.close()
    }
  }, [connect])

  return { connected }
}
