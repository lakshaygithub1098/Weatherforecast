import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import 'leaflet/dist/leaflet.css'

// Components
import { AQIMap } from './components/AQIMap'
import { AQIDetailCard } from './components/AQIDetailCard'
import { LoadingSpinner, ErrorAlert } from './components/LoadingAndStates'
import { Header, StationSearch, StatsCard, Footer } from './components/UI'

// Services & Utils
import { predictionsAPI } from './services/api'
import { getAQICategory } from './utils/aqi'

// Styles
import './index.css'

export default function App() {
  const [stations, setStations] = useState([])
  const [predictions, setPredictions] = useState({})
  const [selectedStation, setSelectedStation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiConnected, setApiConnected] = useState(false)

  // Load stations on mount
  useEffect(() => {
    loadStations()
    checkApiHealth()
  }, [])

  // Auto-predict when station is selected
  useEffect(() => {
    if (selectedStation) {
      predictAQI(selectedStation)
    }
  }, [selectedStation])

  // Periodically refresh predictions for all stations
  useEffect(() => {
    if (stations.length === 0) return

    const interval = setInterval(() => {
      stations.forEach(station => {
        loadPrediction(station)
      })
    }, 5 * 60 * 1000) // 5 minutes

    return () => clearInterval(interval)
  }, [stations])

  const checkApiHealth = async () => {
    try {
      await predictionsAPI.health()
      setApiConnected(true)
    } catch (err) {
      setApiConnected(false)
      console.error('API health check failed:', err)
    }
  }

  const loadStations = async () => {
    try {
      setLoading(true)
      const data = await predictionsAPI.getStations()
      setStations(data)
      setError(null)

      // Load initial predictions for all stations
      data.forEach(station => {
        loadPrediction(station)
      })
    } catch (err) {
      setError('Failed to load stations: ' + (err.message || 'Unknown error'))
      console.error('Error loading stations:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadPrediction = async (station) => {
    try {
      const data = await predictionsAPI.predict(
        station.latitude,
        station.longitude,
        station.name
      )
      setPredictions(prev => ({
        ...prev,
        [station.name]: data
      }))
    } catch (err) {
      console.error(`Error loading prediction for ${station.name}:`, err)
    }
  }

  const predictAQI = async (station) => {
    try {
      setLoading(true)
      setError(null)
      await loadPrediction(station)
    } catch (err) {
      setError('Failed to get prediction: ' + (err.message || 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    await Promise.all(stations.map(s => loadPrediction(s)))
  }

  // Calculate statistics
  const aqiValues = Object.values(predictions).map(p => p.aqi || 0)
  const avgAqi = aqiValues.length > 0 ? (aqiValues.reduce((a, b) => a + b) / aqiValues.length) : 0
  const maxAqi = aqiValues.length > 0 ? Math.max(...aqiValues) : 0
  const minAqi = aqiValues.length > 0 ? Math.min(...aqiValues) : 0

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Header apiStatus={apiConnected} onRefresh={handleRefresh} />
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {error && (
            <div className="mb-6">
              <ErrorAlert
                message={error}
                onDismiss={() => setError(null)}
              />
            </div>
          )}
        </AnimatePresence>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          <StatsCard
            label="Average AQI"
            value={avgAqi.toFixed(1)}
            icon="📊"
          />
          <StatsCard
            label="Highest AQI"
            value={maxAqi.toFixed(1)}
            icon="📈"
          />
          <StatsCard
            label="Lowest AQI"
            value={minAqi.toFixed(1)}
            icon="📉"
          />
          <StatsCard
            label="Stations"
            value={stations.length}
            icon="📍"
          />
        </motion.div>

        {/* Main Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Map */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-lg shadow-lg overflow-hidden"
            >
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-xl font-bold text-gray-800">📍 AQI Map</h2>
              </div>

              {loading && stations.length === 0 ? (
                <div className="h-96">
                  <LoadingSpinner text="Loading map..." />
                </div>
              ) : (
                <AQIMap
                  stations={stations}
                  predictions={predictions}
                  selectedStation={selectedStation}
                  onStationSelect={setSelectedStation}
                  showWindArrows={true}
                />
              )}
            </motion.div>
          </div>

          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            {/* Station Search */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-lg font-bold text-gray-800 mb-4">🔍 Stations</h2>
              <StationSearch
                stations={stations}
                selectedStation={selectedStation}
                onStationSelect={setSelectedStation}
                isLoading={loading}
              />
            </div>

            {/* Detail Card */}
            <div className="bg-white rounded-lg shadow-lg p-4 max-h-96 overflow-y-auto">
              {loading ? (
                <LoadingSpinner text="Loading details..." />
              ) : selectedStation && predictions[selectedStation.name] ? (
                <AQIDetailCard
                  prediction={predictions[selectedStation.name]}
                  station={selectedStation}
                />
              ) : (
                <div className="text-center text-gray-500 py-8">
                  {stations.length === 0 ? (
                    <p>No stations available</p>
                  ) : (
                    <p>Select a station to view details</p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  )
}
