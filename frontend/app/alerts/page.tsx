'use client'

import { useEffect, useState } from 'react'
import { AlertRule, CreateAlertRequest } from '@/types/alerts'
import { Symbol } from '@/types/market'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertRule[]>([])
  const [symbols, setSymbols] = useState<Symbol[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [createForm, setCreateForm] = useState<CreateAlertRequest>({
    symbol: '',
    kind: 'price_above',
    threshold: 0,
    enabled: true,
  })

  // Fetch alerts and symbols
  useEffect(() => {
    async function fetchData() {
      try {
        const [alertsRes, symbolsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/alerts`),
          fetch(`${API_BASE_URL}/api/symbols`),
        ])

        if (!alertsRes.ok) {
          throw new Error('Failed to fetch alerts')
        }
        if (!symbolsRes.ok) {
          throw new Error('Failed to fetch symbols')
        }

        const alertsData: AlertRule[] = await alertsRes.json()
        const symbolsData: Symbol[] = await symbolsRes.json()

        setAlerts(alertsData)
        setSymbols(symbolsData)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createForm),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to create alert')
      }

      const newAlert: AlertRule = await response.json()
      setAlerts([...alerts, newAlert])
      setShowCreateForm(false)
      setCreateForm({
        symbol: '',
        kind: 'price_above',
        threshold: 0,
        enabled: true,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const handleToggleAlert = async (alertId: string, enabled: boolean) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts/${alertId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: !enabled }),
      })

      if (!response.ok) {
        throw new Error('Failed to update alert')
      }

      const updated: AlertRule = await response.json()
      setAlerts(alerts.map((a) => (a.id === alertId ? updated : a)))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const handleDeleteAlert = async (alertId: string) => {
    if (!confirm('Are you sure you want to delete this alert?')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts/${alertId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete alert')
      }

      setAlerts(alerts.filter((a) => a.id !== alertId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const handleTestAlert = async (alertId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts/${alertId}/test`, {
        method: 'POST',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to send test alert')
      }

      alert('Test alert sent! Check your Slack notifications.')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to send test alert')
    }
  }

  const formatKind = (kind: string) => {
    const labels: Record<string, string> = {
      price_above: 'Price Above',
      price_below: 'Price Below',
      pct_move: 'Percentage Move',
    }
    return labels[kind] || kind
  }

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-600">Loading alerts...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Alerts</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Create Alert Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            {showCreateForm ? 'Cancel' : '+ Create Alert'}
          </button>
        </div>

        {/* Create Alert Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4">Create New Alert</h2>
            <form onSubmit={handleCreateAlert}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Symbol
                  </label>
                  <select
                    value={createForm.symbol}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, symbol: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    required
                  >
                    <option value="">Select a symbol</option>
                    {symbols.map((symbol) => (
                      <option key={symbol.symbol} value={symbol.symbol}>
                        {symbol.symbol} {symbol.name && `(${symbol.name})`}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Alert Type
                  </label>
                  <select
                    value={createForm.kind}
                    onChange={(e) =>
                      setCreateForm({
                        ...createForm,
                        kind: e.target.value as CreateAlertRequest['kind'],
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    required
                  >
                    <option value="price_above">Price Above</option>
                    <option value="price_below">Price Below</option>
                    <option value="pct_move">Percentage Move</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Threshold
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={createForm.threshold}
                    onChange={(e) =>
                      setCreateForm({
                        ...createForm,
                        threshold: parseFloat(e.target.value) || 0,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder={
                      createForm.kind === 'pct_move' ? 'e.g., 5.0 (for 5%)' : 'e.g., 50000.0'
                    }
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Create Alert
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Alerts List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Active Alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-gray-600">No alerts configured. Create one above!</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Threshold
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {alerts.map((alert) => (
                    <tr key={alert.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {alert.symbol}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatKind(alert.kind)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {alert.kind === 'pct_move'
                            ? `${alert.threshold}%`
                            : `$${alert.threshold.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}`}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleToggleAlert(alert.id, alert.enabled)}
                          className={`px-3 py-1 rounded text-sm font-medium ${
                            alert.enabled
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {alert.enabled ? 'Enabled' : 'Disabled'}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleTestAlert(alert.id)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            Test
                          </button>
                          <button
                            onClick={() => handleDeleteAlert(alert.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </div>
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

