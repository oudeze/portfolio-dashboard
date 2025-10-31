'use client'

import { useCallback, useEffect, useState } from 'react'
import { Symbol, Quote } from '@/types/market'
import { useWebSocket } from '@/hooks/useWebSocket'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const USE_WEBSOCKET = process.env.NEXT_PUBLIC_USE_WEBSOCKET !== 'false' // Default to true

export default function WatchlistPage() {
  const [symbols, setSymbols] = useState<Symbol[]>([])
  const [quotes, setQuotes] = useState<Record<string, Quote>>({})
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // WebSocket quote handler
  const handleQuote = useCallback((quote: Quote) => {
    setQuotes((prev) => ({
      ...prev,
      [quote.symbol]: quote,
    }))
  }, [])

  // WebSocket connection
  const { connected: wsConnected, error: wsError } = useWebSocket(
    USE_WEBSOCKET ? selectedSymbols : [],
    handleQuote
  )

  // Fetch available symbols on mount
  useEffect(() => {
    async function fetchSymbols() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/symbols`)
        if (!response.ok) {
          throw new Error('Failed to fetch symbols')
        }
        const data: Symbol[] = await response.json()
        setSymbols(data)
        // Default to first 3 symbols
        setSelectedSymbols(data.slice(0, 3).map(s => s.symbol))
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setLoading(false)
      }
    }

    fetchSymbols()
  }, [])

  // Poll quotes for selected symbols (fallback when WebSocket not used)
  useEffect(() => {
    if (USE_WEBSOCKET || selectedSymbols.length === 0) return

    let intervalId: NodeJS.Timeout

    async function pollQuotes() {
      try {
        const promises = selectedSymbols.map(async (symbol) => {
          const response = await fetch(
            `${API_BASE_URL}/api/quotes/latest?symbol=${encodeURIComponent(symbol)}`
          )
          if (!response.ok) {
            throw new Error(`Failed to fetch quote for ${symbol}`)
          }
          const quote: Quote = await response.json()
          return { symbol, quote }
        })

        const results = await Promise.all(promises)
        const newQuotes: Record<string, Quote> = {}
        results.forEach(({ symbol, quote }) => {
          newQuotes[symbol] = quote
        })
        setQuotes(newQuotes)
      } catch (err) {
        console.error('Error polling quotes:', err)
      }
    }

    // Poll immediately, then every 2 seconds
    pollQuotes()
    intervalId = setInterval(pollQuotes, 2000)

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [selectedSymbols])

  const toggleSymbol = (symbol: string) => {
    setSelectedSymbols((prev) => {
      if (prev.includes(symbol)) {
        return prev.filter((s) => s !== symbol)
      } else {
        return [...prev, symbol]
      }
    })
  }

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price)
  }

  const formatTimestamp = (ts: string): string => {
    return new Date(ts).toLocaleTimeString()
  }

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-600">Loading symbols...</p>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-600 font-semibold">Error:</p>
            <p className="text-red-600">{error}</p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Watchlist</h1>

        {/* Symbol selector */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Available Symbols</h2>
          <div className="flex flex-wrap gap-2">
            {symbols.map((symbol) => (
              <button
                key={symbol.symbol}
                onClick={() => toggleSymbol(symbol.symbol)}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  selectedSymbols.includes(symbol.symbol)
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {symbol.symbol} {symbol.name && `(${symbol.name})`}
              </button>
            ))}
          </div>
        </div>

        {/* Connection status */}
        {USE_WEBSOCKET && (
          <div className="bg-white rounded-lg shadow p-4 mb-4">
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
              </span>
              {wsError && (
                <span className="text-sm text-red-600 ml-2">{wsError}</span>
              )}
            </div>
          </div>
        )}

        {/* Quotes table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Current Quotes</h2>
          {selectedSymbols.length === 0 ? (
            <p className="text-gray-600">Select symbols above to view quotes</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Update
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {selectedSymbols.map((symbol) => {
                    const quote = quotes[symbol]
                    const symbolInfo = symbols.find((s) => s.symbol === symbol)
                    return (
                      <tr key={symbol}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {symbol}
                          </div>
                          {symbolInfo?.name && (
                            <div className="text-sm text-gray-500">
                              {symbolInfo.name}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-semibold text-gray-900">
                            {quote ? formatPrice(quote.price) : 'Loading...'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {quote ? formatTimestamp(quote.ts) : '-'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}

