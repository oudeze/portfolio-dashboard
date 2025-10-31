'use client'

import { useEffect, useState } from 'react'
import { PnLSummary } from '@/types/journal'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function PnLPage() {
  const [summary, setSummary] = useState<PnLSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPnL() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/pnl/daily`)
        if (!response.ok) {
          throw new Error('Failed to fetch P&L summary')
        }
        const data: PnLSummary[] = await response.json()
        setSummary(data)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setLoading(false)
      }
    }

    fetchPnL()
    // Refresh every 30 seconds
    const interval = setInterval(fetchPnL, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price)
  }

  const formatPnL = (pnl: number): string => {
    const formatted = formatPrice(pnl)
    return pnl >= 0 ? `+${formatted}` : formatted
  }

  const calculateTotals = () => {
    const totals = summary.reduce(
      (acc, item) => ({
        unrealized: acc.unrealized + item.unrealized_pnl,
        realized: acc.realized + item.realized_pnl,
        total: acc.total + item.total_pnl,
      }),
      { unrealized: 0, realized: 0, total: 0 }
    )
    return totals
  }

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-600">Loading P&L summary...</p>
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

  const totals = calculateTotals()

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">P&L Summary</h1>

        {/* Total Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Realized P&L
            </h3>
            <p
              className={`text-2xl font-bold ${
                totals.realized >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {formatPnL(totals.realized)}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Unrealized P&L
            </h3>
            <p
              className={`text-2xl font-bold ${
                totals.unrealized >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {formatPnL(totals.unrealized)}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total P&L
            </h3>
            <p
              className={`text-2xl font-bold ${
                totals.total >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {formatPnL(totals.total)}
            </p>
          </div>
        </div>

        {/* Positions Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Positions</h2>
          {summary.length === 0 ? (
            <p className="text-gray-600">
              No open positions. Add trades in the journal to see P&L.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unrealized P&L
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Realized P&L
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total P&L
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {summary.map((item) => (
                    <tr key={item.symbol}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {item.symbol}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.qty}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPrice(item.avg_price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPrice(item.current_price)}
                      </td>
                      <td
                        className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                          item.unrealized_pnl >= 0
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {formatPnL(item.unrealized_pnl)}
                      </td>
                      <td
                        className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                          item.realized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {formatPnL(item.realized_pnl)}
                      </td>
                      <td
                        className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${
                          item.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {formatPnL(item.total_pnl)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}

