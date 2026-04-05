import React, { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getAQIColor } from '../utils/aqi'
import { ForecastChart } from './ForecastChart'

// Fix default marker icon (Leaflet issue)
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

/**
 * Create custom Leaflet marker for AQI stations
 */
const createAQIMarkerIcon = (aqi, isSelected) => {
  const color = getAQIColor(aqi)
  const size = isSelected ? 45 : 35
  const iconSize = isSelected ? [45, 45] : [35, 35]

  return L.divIcon({
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background-color: ${color};
        border: 3px solid white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${isSelected ? '14px' : '12px'};
        box-shadow: ${isSelected ? '0 0 10px rgba(59, 130, 246, 0.7), 0 4px 10px rgba(0, 0, 0, 0.4)' : '0 3px 8px rgba(0, 0, 0, 0.3)'};
        transition: all 0.2s ease;
      ">
        ${Math.round(aqi)}
      </div>
    `,
    className: 'aqi-marker',
    iconSize: iconSize,
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size],
  })
}

/**
 * AQI Map Component using Leaflet (OpenStreetMap)
 */
export const AQIMap = ({ stations, predictions, selectedStation, onStationSelect, showWindArrows = true }) => {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const markersRef = useRef({})
  const [showForecast, setShowForecast] = useState(false)

  const defaultCenter = [28.7041, 77.1025] // Delhi center [lat, lng]
  const defaultZoom = 11

  // Initialize map
  useEffect(() => {
    if (mapInstanceRef.current) return // Already initialized

    if (!mapRef.current) {
      console.error('Map container not found')
      return
    }

    // Create Leaflet map
    mapInstanceRef.current = L.map(mapRef.current).setView(defaultCenter, defaultZoom)

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
      minZoom: 5,
    }).addTo(mapInstanceRef.current)

    // Add fullscreen control
    const fullscreenButton = L.control({ position: 'topright' })
    fullscreenButton.onAdd = function () {
      const div = L.DomUtil.create('div', 'leaflet-control leaflet-bar')
      const link = L.DomUtil.create('a', '', div)
      link.href = '#'
      link.title = 'Fullscreen'
      link.innerHTML = '⛶'
      link.onclick = function (e) {
        L.DomEvent.preventDefault(e)
        if (mapRef.current.requestFullscreen) {
          mapRef.current.requestFullscreen()
        }
      }
      return div
    }
    fullscreenButton.addTo(mapInstanceRef.current)

    console.log('✅ Leaflet map initialized successfully')

    return () => {
      // Cleanup
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [])

  // Add/update markers when stations or predictions change
  useEffect(() => {
    if (!mapInstanceRef.current || !stations || stations.length === 0) {
      console.warn('No map instance or stations available')
      return
    }

    // Remove old markers
    Object.values(markersRef.current).forEach(marker => marker.remove())
    markersRef.current = {}

    // Add new markers
    stations.forEach(station => {
      try {
        const prediction = predictions?.[station.name]
        const aqi = prediction?.aqi || 0
        const isSelected = selectedStation?.name === station.name

        const markerIcon = createAQIMarkerIcon(aqi, isSelected)

        const marker = L.marker(
          [station.latitude, station.longitude],
          { icon: markerIcon }
        ).addTo(mapInstanceRef.current)

        // Create popup content
        const popupContent = document.createElement('div')
        popupContent.style.cssText = 'font-family: system-ui, -apple-system, sans-serif; min-width: 280px;'
        popupContent.innerHTML = `
          <div style="padding: 12px;">
            <h3 style="font-weight: bold; margin: 0 0 8px 0; color: #1f2937; font-size: 15px;">
              📍 ${station.name}
            </h3>
            <p style="font-size: 12px; color: #6b7280; margin: 0 0 12px 0;">${station.region}</p>
            
            ${prediction ? `
              <div style="background-color: #f3f4f6; padding: 8px; border-radius: 6px; margin-bottom: 8px;">
                <p style="margin: 6px 0; color: #374151; font-size: 13px;">
                  <span style="font-weight: 600;">AQI Reading:</span> 
                  <span style="color: ${getAQIColor(aqi)}; font-weight: bold; font-size: 16px;">${prediction.aqi.toFixed(1)}</span>
                </p>
              </div>
              
              <div style="font-size: 12px; color: #374151; line-height: 1.6;">
                <p style="margin: 4px 0;"><span style="font-weight: 600;">🌡️ Temperature:</span> ${prediction.weather.temperature.toFixed(1)}°C</p>
                <p style="margin: 4px 0;"><span style="font-weight: 600;">💨 Wind Speed:</span> ${prediction.weather.wind_speed.toFixed(1)} m/s</p>
                <p style="margin: 4px 0;"><span style="font-weight: 600;">💧 Humidity:</span> ${prediction.weather.humidity}%</p>
                <p style="margin: 4px 0;"><span style="font-weight: 600;">🔵 Confidence:</span> ${(prediction.model_confidence?.xgboost * 100).toFixed(0)}%</p>
              </div>
            ` : `
              <div style="background-color: #fef3c7; padding: 8px; border-radius: 6px; border-left: 3px solid #f59e0b;">
                <p style="margin: 0; color: #925311; font-size: 12px;">⏳ Loading prediction data...</p>
              </div>
            `}
            
            <button onclick="this.closest('.leaflet-popup').style.display = 'none'" 
              style="
                width: 100%;
                margin-top: 8px;
                padding: 6px 12px;
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
              ">
              View Details
            </button>
          </div>
        `

        marker.bindPopup(popupContent, { maxWidth: 350, maxHeight: 400 })

        // Click handler
        marker.on('click', () => {
          onStationSelect(station)
          marker.openPopup()
        })

        // Auto-open popup for selected station
        if (isSelected) {
          marker.openPopup()
        }

        markersRef.current[station.name] = marker
        console.log(`✅ Marker added for ${station.name}`)
      } catch (error) {
        console.error(`Error creating marker for ${station.name}:`, error)
      }
    })

    console.log(`✅ Added ${stations.length} markers to map`)
  }, [stations, predictions, selectedStation, onStationSelect])

  return (
    <div className="relative w-full h-full rounded-lg overflow-hidden shadow-lg bg-gray-100">
      {/* Map Container */}
      <div
        ref={mapRef}
        className="w-full h-full z-0"
        style={{ minHeight: '600px', background: '#e5e7eb' }}
      />

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-md p-4 z-10 text-sm max-w-xs">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
          📊 AQI Levels
        </h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#2ecc71' }}></div>
            <span className="text-gray-700 text-xs">Good (0-50)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#f1c40f' }}></div>
            <span className="text-gray-700 text-xs">Fair (51-100)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#e67e22' }}></div>
            <span className="text-gray-700 text-xs">Moderate (101-200)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#e74c3c' }}></div>
            <span className="text-gray-700 text-xs">Poor (201-300)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#c0392b' }}></div>
            <span className="text-gray-700 text-xs">Very Poor (301-400)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#8b0000' }}></div>
            <span className="text-gray-700 text-xs">Severe (401+)</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-3 border-t pt-2">Click on markers to see details or forecast</p>
      </div>

      {/* Status Corner */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-md px-3 py-2 z-10 text-xs">
        <p className="text-gray-600">
          📍 <span className="font-semibold">{stations?.length || 0}</span> stations
        </p>
      </div>

      {/* Forecast Chart Modal */}
      {showForecast && selectedStation && (
        <div
          className="absolute bottom-6 left-6 z-20 bg-white rounded-lg shadow-xl"
          style={{ width: 'min(90vw, 800px)', maxHeight: '500px', overflowY: 'auto' }}
        >
          <ForecastChart
            station={selectedStation}
            onClose={() => setShowForecast(false)}
          />
        </div>
      )}

      {/* Forecast Button (appears when station is selected) */}
      {selectedStation && !showForecast && (
        <button
          onClick={() => setShowForecast(true)}
          className="absolute bottom-6 left-6 z-10 px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-600 transition text-sm font-semibold"
        >
          📊 View 24h Forecast
        </button>
      )}
    </div>
  )
}

export default AQIMap
