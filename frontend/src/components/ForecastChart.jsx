import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getAQIColor } from '../utils/aqi'
import axios from 'axios'

/**
 * 24-hour AQI Forecast Chart Component
 */
export const ForecastChart = ({ station, onClose }) => {
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!station) return

    const fetchForecast = async () => {
      try {
        setLoading(true)
        setError(null)

        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await axios.get(
          `${apiUrl}/forecast?station=${encodeURIComponent(station.name)}`
        )

        setForecast(response.data)
      } catch (err) {
        console.error('Forecast fetch error:', err)
        setError(err.response?.data?.detail || 'Failed to load forecast')
      } finally {
        setLoading(false)
      }
    }

    fetchForecast()
  }, [station])

  if (!station) return null

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
          Loading 24-hour forecast for <strong>{station.name}</strong>...
        </div>
        <div
          style={{
            display: 'inline-block',
            width: '30px',
            height: '30px',
            border: '3px solid #ddd',
            borderTop: '3px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }}
        />
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#dc2626' }}>
        ⚠️ {error}
      </div>
    )
  }

  if (!forecast || !forecast.forecast) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        No forecast data available
      </div>
    )
  }

  // Helper function to format time in 12-hour AM/PM format
  const formatTimeAMPM = (timestamp) => {
    const date = new Date(timestamp)
    let hours = date.getHours()
    const ampm = hours >= 12 ? 'PM' : 'AM'
    hours = hours % 12
    hours = hours ? hours : 12 // Convert 0 to 12
    return `${hours}:00 ${ampm}`
  }

  // Format data for chart
  const chartData = forecast.forecast.map(point => ({
    time: formatTimeAMPM(point.timestamp),
    aqi: parseFloat(point.aqi),
    temperature: point.temperature,
    humidity: point.humidity,
    full_timestamp: point.timestamp,
  }))

  // Determine line color based on max AQI in forecast
  const maxAqi = Math.max(...chartData.map(d => d.aqi))
  const lineColor = getAQIColor(maxAqi)

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const level =
        data.aqi <= 50 ? 'Good' :
        data.aqi <= 100 ? 'Fair' :
        data.aqi <= 200 ? 'Moderate' :
        data.aqi <= 300 ? 'Poor' :
        data.aqi <= 400 ? 'Very Poor' : 'Severe'

      return (
        <div
          style={{
            backgroundColor: 'white',
            padding: '8px 12px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
        >
          <p style={{ margin: '4px 0', fontSize: '12px', fontWeight: 'bold' }}>
            {data.time}
          </p>
          <p style={{ margin: '4px 0', fontSize: '12px', color: lineColor }}>
            <strong>AQI: {data.aqi.toFixed(1)}</strong> ({level})
          </p>
          <p style={{ margin: '4px 0', fontSize: '11px', color: '#666' }}>
            🌡️ {data.temperature.toFixed(1)}°C
          </p>
          <p style={{ margin: '4px 0', fontSize: '11px', color: '#666' }}>
            💧 {data.humidity}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div style={{
      padding: '16px',
      width: '100%',
      maxWidth: '800px',
      margin: '0 auto',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>
            📊 24-Hour AQI Forecast
          </h3>
          <p style={{ margin: '0', fontSize: '12px', color: '#6b7280' }}>
            {station.name} • Next 24 hours
          </p>
        </div>
        <button
          onClick={onClose}
          style={{
            padding: '6px 12px',
            background: '#f3f4f6',
            border: '1px solid #ddd',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: '600',
          }}
        >
          ✕ Close
        </button>
      </div>

      {/* Chart */}
      <div style={{
        backgroundColor: '#fafbfc',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '12px',
        marginBottom: '16px',
      }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="time"
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              interval={2}
            />
            <YAxis
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              domain={[0, 'dataMax + 20']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="line"
            />
            <Line
              type="monotone"
              dataKey="aqi"
              stroke={lineColor}
              strokeWidth={3}
              dot={{ fill: lineColor, r: 4 }}
              activeDot={{ r: 6 }}
              name="AQI"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Statistics */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
        <div style={{
          backgroundColor: '#f9fafb',
          padding: '12px',
          borderRadius: '6px',
          border: '1px solid #e5e7eb',
        }}>
          <p style={{ margin: '0 0 4px 0', fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>
            Max AQI
          </p>
          <p style={{
            margin: '0',
            fontSize: '18px',
            fontWeight: 'bold',
            color: lineColor,
          }}>
            {Math.max(...chartData.map(d => d.aqi)).toFixed(1)}
          </p>
        </div>

        <div style={{
          backgroundColor: '#f9fafb',
          padding: '12px',
          borderRadius: '6px',
          border: '1px solid #e5e7eb',
        }}>
          <p style={{ margin: '0 0 4px 0', fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>
            Min AQI
          </p>
          <p style={{
            margin: '0',
            fontSize: '18px',
            fontWeight: 'bold',
            color: getAQIColor(Math.min(...chartData.map(d => d.aqi))),
          }}>
            {Math.min(...chartData.map(d => d.aqi)).toFixed(1)}
          </p>
        </div>

        <div style={{
          backgroundColor: '#f9fafb',
          padding: '12px',
          borderRadius: '6px',
          border: '1px solid #e5e7eb',
        }}>
          <p style={{ margin: '0 0 4px 0', fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>
            Avg AQI
          </p>
          <p style={{
            margin: '0',
            fontSize: '18px',
            fontWeight: 'bold',
            color: getAQIColor((Math.max(...chartData.map(d => d.aqi)) + Math.min(...chartData.map(d => d.aqi))) / 2),
          }}>
            {(chartData.reduce((sum, d) => sum + d.aqi, 0) / chartData.length).toFixed(1)}
          </p>
        </div>
      </div>

      {/* AQI Level Legend */}
      <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f0fdf4', borderLeft: '4px solid #22c55e', borderRadius: '4px' }}>
        <p style={{ margin: '0', fontSize: '12px', color: '#15803d', fontWeight: '600' }}>
          💡 Tip: Click on the chart to see detailed hour-by-hour data
        </p>
      </div>
    </div>
  )
}

export default ForecastChart
