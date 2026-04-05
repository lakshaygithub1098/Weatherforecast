import React from 'react'
import { motion } from 'framer-motion'
import { getAQICategory, getHealthRecommendation } from '../utils/aqi'

/**
 * AQI Detail Card Component
 * Shows detailed information for a selected station
 */
export const AQIDetailCard = ({ prediction, station }) => {
  if (!prediction) {
    return (
      <div className="p-6 bg-gray-100 rounded-lg text-center text-gray-500">
        Click on a station to view details
      </div>
    )
  }

  const category = getAQICategory(prediction.aqi)
  const recommendation = getHealthRecommendation(prediction.aqi)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-lg p-6 space-y-6"
    >
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800">
          {station?.name || 'Station'}
        </h2>
        <p className="text-gray-500 text-sm">
          {station?.latitude.toFixed(4)}, {station?.longitude.toFixed(4)}
        </p>
      </div>

      {/* AQI Display */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm font-medium">Air Quality Index</p>
            <p className="text-5xl font-bold text-gray-800 mt-2">
              {prediction.aqi.toFixed(1)}
            </p>
          </div>
          <div className={`aqi-badge ${category.category}`}>
            {category.label}
          </div>
        </div>
      </div>

      {/* Model Predictions */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-gray-600 text-xs font-semibold uppercase">XGBoost</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {prediction.xgboost_prediction.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Confidence: {(prediction.model_confidence.xgboost * 100).toFixed(0)}%
          </p>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <p className="text-gray-600 text-xs font-semibold uppercase">LSTM</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">
            {prediction.lstm_prediction.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Confidence: {(prediction.model_confidence.lstm * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Weather Data */}
      <div className="border-t border-gray-200 pt-4">
        <h3 className="font-semibold text-gray-800 mb-3">Weather Conditions</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">🌡️</span>
            <div>
              <p className="text-xs text-gray-500">Temperature</p>
              <p className="text-sm font-semibold">
                {prediction.weather.temperature}°C
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-gray-500">💧</span>
            <div>
              <p className="text-xs text-gray-500">Humidity</p>
              <p className="text-sm font-semibold">
                {prediction.weather.humidity}%
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-gray-500">💨</span>
            <div>
              <p className="text-xs text-gray-500">Wind Speed</p>
              <p className="text-sm font-semibold">
                {prediction.weather.wind_speed.toFixed(1)} m/s
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-gray-500">🧭</span>
            <div>
              <p className="text-xs text-gray-500">Wind Direction</p>
              <p className="text-sm font-semibold">
                {prediction.weather.wind_direction}°
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Contributing Factors */}
      {prediction.contributing_factors && (
        <div className="border-t border-gray-200 pt-4">
          <h3 className="font-semibold text-gray-800 mb-3">Contributing Factors</h3>
          <div className="space-y-2">
            {Object.entries(prediction.contributing_factors)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([factor, importance]) => (
                <div key={factor} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 capitalize">
                    {factor.replace(/_/g, ' ')}
                  </span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${Math.min(importance * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Health Recommendation */}
      <div className={`p-4 rounded-lg ${
        category.category === 'good' ? 'bg-green-50' :
        category.category === 'fair' ? 'bg-yellow-50' :
        category.category === 'moderate' ? 'bg-orange-50' :
        'bg-red-50'
      }`}>
        <p className="text-sm font-semibold text-gray-800 mb-1">
          📋 Health Recommendation
        </p>
        <p className="text-sm text-gray-700">
          {recommendation}
        </p>
      </div>

      {/* Timestamp */}
      <div className="text-xs text-gray-400 text-center">
        Updated: {new Date(prediction.timestamp).toLocaleTimeString()}
      </div>
    </motion.div>
  )
}

export default AQIDetailCard
