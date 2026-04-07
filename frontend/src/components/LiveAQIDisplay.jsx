import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { getAQICategory, getWindSector, getWindSpeedDescription } from '../utils/aqiCategories'

/**
 * Live AQI Display Component
 * Shows real-time AQI data from WAQI API (not ML predictions)
 */
export const LiveAQIDisplay = ({ station }) => {
  const [liveData, setLiveData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)

  useEffect(() => {
    if (!station) return

    const fetchLiveAQI = async () => {
      try {
        setLoading(true)
        setError(null)

        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await axios.get(
          `${apiUrl}/live-aqi?station=${encodeURIComponent(station.name)}`
        )

        setLiveData(response.data.aqi_data)
        setLastUpdate(new Date())
      } catch (err) {
        console.error('Live AQI fetch error:', err)
        setError(err.response?.data?.detail || 'Failed to load live AQI')
      } finally {
        setLoading(false)
      }
    }

    fetchLiveAQI()

    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchLiveAQI, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [station])

  if (!station) return null

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
        Loading live AQI data...
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

  if (!liveData) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        No live AQI data available
      </div>
    )
  }

  const category = getAQICategory(liveData.aqi)
  const windSector = getWindSector(liveData.wind_direction || 0)
  const windDesc = getWindSpeedDescription(liveData.wind_speed || 0)

  return (
    <div style={{
      padding: '20px',
      backgroundColor: category.bgColor,
      borderLeft: `4px solid ${category.color}`,
      borderRadius: '4px',
      marginBottom: '20px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h3 style={{ margin: 0, color: category.textColor }}>
          💨 Live Air Quality
        </h3>
        <span style={{ fontSize: '12px', color: '#666' }}>
          Updated: {lastUpdate?.toLocaleTimeString()}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '16px',
        marginBottom: '16px'
      }}>
        {/* AQI Display */}
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
            AQI Index
          </div>
          <div style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: category.color
          }}>
            {liveData.aqi.toFixed(1)}
          </div>
          <div style={{
            fontSize: '12px',
            color: category.textColor,
            marginTop: '4px'
          }}>
            {category.label}
          </div>
        </div>

        {/* Pollutants */}
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
            POLLUTANTS
          </div>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>🟤 PM2.5: <strong>{liveData.pm25?.toFixed(1) || 'N/A'}</strong> µg/m³</div>
            <div>🟫 PM10: <strong>{liveData.pm10?.toFixed(1) || 'N/A'}</strong> µg/m³</div>
            <div>⚫ NO₂: <strong>{liveData.no2?.toFixed(1) || 'N/A'}</strong> ppb</div>
          </div>
        </div>

        {/* Weather */}
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
            WEATHER
          </div>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>🌡️ Temp: <strong>{liveData.temperature?.toFixed(1) || 'N/A'}°C</strong></div>
            <div>💧 Humidity: <strong>{liveData.humidity?.toFixed(0) || 'N/A'}%</strong></div>
          </div>
        </div>

        {/* Wind */}
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
            WIND
          </div>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>💨 Speed: <strong>{liveData.wind_speed?.toFixed(1) || 'N/A'}</strong> m/s ({windDesc})</div>
            <div>🧭 Direction: <strong>{windSector}</strong> ({liveData.wind_direction?.toFixed(0) || 'N/A'}°)</div>
          </div>
        </div>
      </div>

      <div style={{
        fontSize: '11px',
        color: '#666',
        padding: '12px',
        backgroundColor: 'rgba(0, 0, 0, 0.05)',
        borderRadius: '4px'
      }}>
        ℹ️ Live data from WAQI API (World Air Quality Index) | Source: {liveData.source || 'Sensor Network'}
      </div>
    </div>
  )
}

export default LiveAQIDisplay
