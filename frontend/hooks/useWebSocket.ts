/**
 * WebSocket hook for real-time market data.
 */

import { useEffect, useRef, useState } from 'react'
import { Quote } from '@/types/market'

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

interface WebSocketMessage {
  type: 'quote' | 'subscribed' | 'unsubscribed' | 'error' | 'pong'
  data?: Quote
  symbols?: string[]
  message?: string
}

export function useWebSocket(
  subscriptions: string[],
  onQuote: (quote: Quote) => void
) {
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const subscriptionsRef = useRef<string[]>([])

  useEffect(() => {
    subscriptionsRef.current = subscriptions
  }, [subscriptions])

  useEffect(() => {
    if (subscriptions.length === 0) {
      // Close connection if no subscriptions
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
        setConnected(false)
      }
      return
    }

    // Connect to WebSocket
    const ws = new WebSocket(`${WS_BASE_URL}/api/ws/quotes`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      setError(null)
      // Subscribe to symbols
      ws.send(
        JSON.stringify({
          action: 'subscribe',
          symbols: subscriptions,
        })
      )
    }

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)

        if (message.type === 'quote' && message.data) {
          onQuote(message.data)
        } else if (message.type === 'error') {
          setError(message.message || 'Unknown error')
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setError('WebSocket connection error')
      setConnected(false)
    }

    ws.onclose = () => {
      setConnected(false)
      // Will reconnect automatically via useEffect when subscriptions change
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        // Unsubscribe before closing
        ws.send(
          JSON.stringify({
            action: 'unsubscribe',
            symbols: subscriptions,
          })
        )
      }
      ws.close()
    }
  }, [subscriptions, onQuote])

  // Update subscriptions when they change (if WebSocket is open)
  useEffect(() => {
    const ws = wsRef.current
    if (ws && ws.readyState === WebSocket.OPEN && subscriptions.length > 0) {
      // Subscribe to all current subscriptions
      ws.send(
        JSON.stringify({
          action: 'subscribe',
          symbols: subscriptions,
        })
      )
    }
  }, [subscriptions])

  return { connected, error }
}

