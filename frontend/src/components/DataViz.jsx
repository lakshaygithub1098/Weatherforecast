import React from 'react'
import { motion } from 'framer-motion'

/**
 * Confidence Meter Component
 * Shows model confidence with visual indicator
 */
export const ConfidenceMeter = ({ value, label = 'Confidence' }) => {
  const percentage = Math.min(Math.max(value * 100, 0), 100)

  const getColor = () => {
    if (percentage >= 90) return 'bg-green-500'
    if (percentage >= 70) return 'bg-blue-500'
    if (percentage >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-bold text-gray-900">{percentage.toFixed(0)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full ${getColor()}`}
        />
      </div>
    </div>
  )
}

/**
 * Trend Indicator Component
 */
export const TrendIndicator = ({ value, label = 'Trend' }) => {
  const isPositive = value > 0
  const isNeutral = value === 0

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-gray-700">{label}:</span>
      <span className={`font-bold ${
        isNeutral ? 'text-gray-500' :
        isPositive ? 'text-red-500' : 'text-green-500'
      }`}>
        {isNeutral ? '→' : isPositive ? '↑' : '↓'} {Math.abs(value).toFixed(1)}
      </span>
    </div>
  )
}

/**
 * Weather Icon Component
 */
export const WeatherIcon = ({ condition, size = 'md' }) => {
  const iconMap = {
    'Clear': '☀️',
    'Clouds': '☁️',
    'Rain': '🌧️',
    'Drizzle': '🌦️',
    'Thunderstorm': '⛈️',
    'Snow': '❄️',
    'Mist': '🌫️',
    'Smoke': '💨',
    'Haze': '😶‍🌫️',
    'Dust': '🌪️',
    'Fog': '🌫️',
    'Sand': '🌬️',
    'Ash': '🌋',
    'Squall': '💨',
    'Tornado': '🌪️'
  }

  const icon = iconMap[condition] || '🌍'

  const sizeClasses = {
    'sm': 'text-xl',
    'md': 'text-3xl',
    'lg': 'text-5xl'
  }

  return <span className={sizeClasses[size]}>{icon}</span>
}

/**
 * Wind Rose Component
 * Visual representation of wind direction
 */
export const WindRose = ({ direction, speed }) => {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-24 h-24">
        {/* Wind rose background */}
        <svg
          className="w-full h-full"
          viewBox="0 0 100 100"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Compass circle */}
          <circle cx="50" cy="50" r="48" fill="none" stroke="#e5e7eb" strokeWidth="1" />

          {/* Cardinal directions */}
          <text x="50" y="15" textAnchor="middle" className="font-bold text-xs" fill="#1f2937">N</text>
          <text x="85" y="52" textAnchor="middle" className="font-bold text-xs" fill="#1f2937">E</text>
          <text x="50" y="88" textAnchor="middle" className="font-bold text-xs" fill="#1f2937">S</text>
          <text x="15" y="52" textAnchor="middle" className="font-bold text-xs" fill="#1f2937">W</text>

          {/* Wind arrow */}
          <g transform={`rotate(${direction} 50 50)`}>
            <polygon
              points="50,10 46,30 50,26 54,30"
              fill="#3b82f6"
              opacity="0.8"
            />
            <line x1="50" y1="26" x2="50" y2="50" stroke="#3b82f6" strokeWidth="2" />
          </g>
        </svg>

        {/* Center dot */}
        <div className="absolute top-1/2 left-1/2 w-3 h-3 bg-blue-600 rounded-full transform -translate-x-1/2 -translate-y-1/2" />
      </div>

      {/* Speed and direction text */}
      <div className="text-center">
        <p className="text-sm font-semibold text-gray-800">
          {speed.toFixed(1)} m/s
        </p>
        <p className="text-xs text-gray-500">
          {Math.round(direction)}°
        </p>
      </div>
    </div>
  )
}

export default {
  ConfidenceMeter,
  TrendIndicator,
  WeatherIcon,
  WindRose,
}
