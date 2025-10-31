'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Quote } from '@/types/market'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SymbolChartPage() {
  const params = useParams()
  const symbol = params.symbol as string
  
  const [priceData, setPriceData] = useState<Array<{ time: string; price: number }>>([])
  const [currentQuote, setCurrentQuote] = useState<Quote | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!symbol) return

    // Fetch initial quote
    async function fetchQuote() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/quotes/latest?symbol=${encodeURIComponent(symbol)}`
        )
        if (response.ok) {
          const quote: Quote = await response.json()
          setCurrentQuote(quote)
          
          // Add to price data
          setPriceData((prev) => {
            const newData = [
              ...prev,
              {
                time: new Date(quote.ts).toLocaleTimeString(),
                price: quote.price,
              },
            ]
            // Keep last 50 data points
            return newData.slice(-50)
          })
        }
      } catch (err) {
        console.error('Error fetching quote:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchQuote()

    // Poll for updates every 2 seconds
    const interval = setInterval(fetchQuote, 2000)

    return () => clearInterval(interval)
  }, [symbol])

  // Calculate simple moving averages
  const calculateSMA = (period: number) => {
    if (priceData.length < period) return []
    const sma = []
    for (let i = period - 1; i < priceData.length; i++) {
      const sum = priceData.slice(i - period + 1, i + 1).reduce((acc, d) => acc + d.price, 0)
      sma.push({ time: priceData[i].time, value: sum / period })
    }
    return sma
  }

  const ema20 = calculateSMA(20)
  const ema50 = calculateSMA(50)

  // Calculate RSI
  const calculateRSI = (period: number = 14) => {
    if (priceData.length < period + 1) return []
    const rsi = []
    for (let i = period; i < priceData.length; i++) {
      const prices = priceData.slice(i - period, i + 1).map((d) => d.price)
      let gains = 0
      let losses = 0
      
      for (let j = 1; j < prices.length; j++) {
        const change = prices[j] - prices[j - 1]
        if (change > 0) gains += change
        else losses += Math.abs(change)
      }
      
      const avgGain = gains / period
      const avgLoss = losses / period
      const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
      const rsiValue = 100 - (100 / (1 + rs))
      
      rsi.push({ time: priceData[i].time, value: rsiValue })
    }
    return rsi
  }

  const rsi = calculateRSI(14)

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-600">Loading chart data...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">{symbol} Chart</h1>

        {currentQuote && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Current Price</p>
                <p className="text-2xl font-bold">
                  ${currentQuote.price.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Update</p>
                <p className="text-lg">{new Date(currentQuote.ts).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Data Points</p>
                <p className="text-lg">{priceData.length}</p>
              </div>
            </div>
          </div>
        )}

        {/* Price Chart with EMA */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Price Chart</h2>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Price"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* EMA Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4">Moving Averages</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Price"
                />
                {ema20.length > 0 && (
                  <Line
                    type="monotone"
                    data={ema20}
                    dataKey="value"
                    stroke="#10b981"
                    strokeWidth={1}
                    strokeDasharray="5 5"
                    name="EMA(20)"
                  />
                )}
                {ema50.length > 0 && (
                  <Line
                    type="monotone"
                    data={ema50}
                    dataKey="value"
                    stroke="#f59e0b"
                    strokeWidth={1}
                    strokeDasharray="5 5"
                    name="EMA(50)"
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* RSI Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4">RSI (14)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={rsi}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  name="RSI"
                />
                {/* Overbought/Oversold lines */}
                <Line
                  type="monotone"
                  dataKey=""
                  stroke="#ef4444"
                  strokeDasharray="3 3"
                  strokeWidth={1}
                  name="Overbought (70)"
                  data={rsi.map(() => ({ time: '', value: 70 }))}
                />
                <Line
                  type="monotone"
                  dataKey=""
                  stroke="#22c55e"
                  strokeDasharray="3 3"
                  strokeWidth={1}
                  name="Oversold (30)"
                  data={rsi.map(() => ({ time: '', value: 30 }))}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </main>
  )
}

