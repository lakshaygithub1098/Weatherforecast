import React from 'react'
import { motion } from 'framer-motion'

/**
 * Header Component with API Status
 */
export const Header = ({ apiStatus = null, onRefresh = null }) => {
  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 rounded-lg shadow-lg"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">🌍 Delhi AQI Dashboard</h1>
          <p className="text-blue-100 text-sm mt-1">
            Real-time air quality monitoring with ML predictions
          </p>
        </div>

        <div className="flex items-center gap-4">
          {apiStatus !== null && (
            <div className="flex items-center gap-2 bg-blue-700 px-4 py-2 rounded-lg">
              <div className={`w-3 h-3 rounded-full ${apiStatus ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm font-medium">
                {apiStatus ? 'API Connected' : 'API Disconnected'}
              </span>
            </div>
          )}

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="bg-blue-700 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              🔄 Refresh
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

/**
 * Station Filter/Search Component
 */
export const StationSearch = ({ stations, selectedStation, onStationSelect, isLoading = false }) => {
  const [searchTerm, setSearchTerm] = React.useState('')

  const filteredStations = stations?.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.region.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  return (
    <div className="space-y-3">
      <input
        type="text"
        placeholder="Search stations..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        disabled={isLoading}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
      />

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {filteredStations.map(station => (
          <motion.button
            key={station.name}
            whileHover={{ scale: 1.02 }}
            onClick={() => onStationSelect(station)}
            className={`w-full text-left p-3 rounded-lg transition-colors ${
              selectedStation?.name === station.name
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
            }`}
          >
            <div className="font-semibold">{station.name}</div>
            <div className="text-xs opacity-75">{station.region}</div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}

/**
 * Statistics Card Component
 */
export const StatsCard = ({ label, value, unit, icon, trend = null }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-lg transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{label}</p>
          <div className="flex items-baseline gap-2 mt-2">
            <p className="text-2xl font-bold text-gray-800">{value}</p>
            {unit && <p className="text-gray-500 text-sm">{unit}</p>}
          </div>
          {trend && (
            <p className={`text-xs mt-2 ${trend > 0 ? 'text-red-500' : 'text-green-500'}`}>
              {trend > 0 ? '📈' : '📉'} {Math.abs(trend).toFixed(1)}% vs yesterday
            </p>
          )}
        </div>
        {icon && <span className="text-3xl">{icon}</span>}
      </div>
    </motion.div>
  )
}

/**
 * Footer Component
 */
export const Footer = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 py-6 px-4 mt-12">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
          <div>
            <h3 className="font-bold text-white mb-2">About</h3>
            <p className="text-sm">
              Real-time AQI prediction system using XGBoost and LSTM models with live weather data.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-white mb-2">Data Sources</h3>
            <ul className="text-sm space-y-1">
              <li>• OpenWeatherMap API</li>
              <li>• Delhi Pollution Board</li>
              <li>• Weather Monitoring Stations</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-white mb-2">Models</h3>
            <ul className="text-sm space-y-1">
              <li>• XGBoost (70% weight)</li>
              <li>• LSTM Neural Network (30% weight)</li>
              <li>• Ensemble Average</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 pt-6 text-center text-sm">
          <p>
            Built with ❤️ | FastAPI Backend + React Frontend | Last updated:{' '}
            {new Date().toLocaleString()}
          </p>
          <p className="mt-2 text-xs text-gray-500">
            Data is updated every 5 minutes | Cache TTL: 5 minutes
          </p>
        </div>
      </div>
    </footer>
  )
}

export default {
  Header,
  StationSearch,
  StatsCard,
  Footer,
}
