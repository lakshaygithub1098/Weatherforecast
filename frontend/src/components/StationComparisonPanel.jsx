import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { getAQICategory, getAQIColor } from '../utils/aqiCategories'

/**
 * Station Comparison Panel Component
 * Displays all stations ranked by current AQI
 * Shows which stations influence the selected station
 * 
 * Props:
 * - selectedStation: Currently selected station name
 * - stationList: Array of station objects with name, latitude, longitude
 * - apiBaseUrl: Backend API base URL
 */
export const StationComparisonPanel = ({ selectedStation, stationList, apiBaseUrl = 'http://localhost:8000' }) => {
  const [allStations, setAllStations] = useState([])
  const [upwindStations, setUpwindStations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchComparisonData()
  }, [selectedStation])

  const fetchComparisonData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all live AQI data
      const allAqiResponse = await axios.get(`${apiBaseUrl}/all-live-aqi`)
      const allAqiData = allAqiResponse.data.stations || []

      // Sort by AQI descending (worst first)
      const sorted = allAqiData.sort((a, b) => (b.aqi || 0) - (a.aqi || 0))
      setAllStations(sorted)

      // Fetch debug data for selected station to get upwind info
      if (selectedStation) {
        try {
          const debugResponse = await axios.get(`${apiBaseUrl}/debug?station=${selectedStation}`)
          const upwindData = debugResponse.data.upwind_influence || []
          setUpwindStations(upwindData)
        } catch (err) {
          console.warn('Could not fetch upwind data:', err.message)
          setUpwindStations([])
        }
      }
    } catch (err) {
      console.error('Error fetching comparison data:', err)
      setError('Failed to load station comparison data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="w-full bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Station Comparison</h3>
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin">
            <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Station Comparison</h3>
        <div className="text-red-600 text-sm">{error}</div>
      </div>
    )
  }

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Station Comparison</h3>

      {/* Selected Station Info */}
      {selectedStation && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2">Selected: {selectedStation}</h4>
          
          {upwindStations.length > 0 && (
            <div className="mt-3">
              <p className="text-sm text-blue-800 font-medium mb-2">
                🌬️ Upwind Influence ({upwindStations.length} stations):
              </p>
              <div className="flex flex-wrap gap-2">
                {upwindStations.map((station, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-200 text-blue-900 rounded-full text-sm font-medium"
                  >
                    {station.name} ({station.influence_score?.toFixed(2) || 'N/A'})
                  </span>
                ))}
              </div>
            </div>
          )}

          {upwindStations.length === 0 && (
            <p className="text-sm text-blue-700 italic">No upwind influence data available</p>
          )}
        </div>
      )}

      {/* All Stations Ranked List */}
      <div>
        <h4 className="font-semibold text-gray-700 mb-3 flex items-center">
          <span className="mr-2">🏪</span>
          All Stations (Ranked by Current AQI)
        </h4>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {allStations.map((station, index) => {
            const category = getAQICategory(station.aqi || 100)
            const color = getAQIColor(station.aqi || 100)
            const isSelected = station.name === selectedStation
            const isUpwind = upwindStations.some(s => s.name === station.name)

            return (
              <div
                key={index}
                className={`
                  p-3 rounded-lg flex items-center justify-between
                  ${isSelected ? 'bg-blue-100 border-2 border-blue-500' : 'bg-gray-50'}
                  ${isUpwind ? 'border-2 border-orange-400' : ''}
                  hover:bg-gray-100 transition-colors cursor-pointer
                `}
              >
                <div className="flex-1 flex items-center gap-3">
                  {/* Rank Badge */}
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center font-bold text-sm">
                    {index + 1}
                  </div>

                  {/* Station Name */}
                  <div className="flex-1">
                    <p className="font-medium text-gray-800">
                      {station.name}
                      {isSelected && <span className="ml-2 text-blue-600 text-sm">(Selected)</span>}
                      {isUpwind && <span className="ml-2 text-orange-600 text-sm font-bold">⬆️ Upwind</span>}
                    </p>
                    <p className="text-xs text-gray-600">
                      {station.pm25 ? `PM2.5: ${station.pm25.toFixed(0)} µg/m³` : 'N/A'}
                    </p>
                  </div>
                </div>

                {/* AQI Display */}
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <p
                      className="text-2xl font-bold"
                      style={{ color: color }}
                    >
                      {(station.aqi || 100).toFixed(0)}
                    </p>
                    <p className="text-xs text-gray-600 uppercase">
                      {category}
                    </p>
                  </div>

                  {/* Color indicator dot */}
                  <div
                    className="w-4 h-4 rounded-full shadow-md"
                    style={{ backgroundColor: color }}
                    title={category}
                  ></div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-600 font-semibold mb-2">Legend:</p>
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-100 border-2 border-blue-500 rounded"></div>
            <span>Selected Station</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 border-2 border-orange-400 rounded"></div>
            <span>Upwind Influence</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StationComparisonPanel
