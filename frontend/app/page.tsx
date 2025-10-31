'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface HealthResponse {
  status: string
  service: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`)
        if (!response.ok) {
          throw new Error('Failed to fetch health status')
        }
        const data: HealthResponse = await response.json()
        setHealth(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
  }, [])

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Market Data Dashboard</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Backend Status</h2>
          
          {loading && (
            <p className="text-gray-600">Checking backend connection...</p>
          )}
          
          {error && (
            <div className="text-red-600">
              <p className="font-semibold">Error:</p>
              <p>{error}</p>
            </div>
          )}
          
          {health && (
            <div className="text-green-600">
              <p className="font-semibold">Status: {health.status}</p>
              <p className="text-sm text-gray-600">Service: {health.service}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Navigation</h2>
          <div className="flex gap-4">
            <Link
              href="/watchlist"
              className="inline-block bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Watchlist →
            </Link>
            <Link
              href="/alerts"
              className="inline-block bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors"
            >
              Alerts →
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}

