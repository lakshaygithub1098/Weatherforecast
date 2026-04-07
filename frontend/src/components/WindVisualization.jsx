import React, { useEffect } from 'react'
import L from 'leaflet'
import { getAQIColor } from '../utils/aqiCategories'

/**
 * Wind Visualization Component
 * Draws animated arrows between stations showing wind direction and pollution flow
 */
export const WindVisualization = ({ map, stations, stationAQI, windData }) => {
  useEffect(() => {
    if (!map || !stations || !stationAQI || !windData) return

    // Clear existing wind arrows
    map.eachLayer((layer) => {
      if (layer._windArrow) {
        map.removeLayer(layer)
      }
    })

    // Draw wind arrows for each station pair based on wind direction
    stations.forEach((sourceStation) => {
      const sourceAQI = stationAQI[sourceStation.name]
      if (!sourceAQI) return

      const sourceWind = windData[sourceStation.name]
      if (!sourceWind) return

      // Find nearby stations that would be downwind
      stations.forEach((targetStation) => {
        if (sourceStation.name === targetStation.name) return

        // Calculate if target is downwind of source based on wind direction
        const bearing = calculateBearing(
          sourceStation.latitude, sourceStation.longitude,
          targetStation.latitude, targetStation.longitude
        )

        // Wind FROM direction means particles move from source to target
        // if bearing aligns with wind direction
        const windDir = sourceWind.wind_direction || 0
        const angleDiff = Math.abs(bearing - windDir)
        const normalizedAngleDiff = Math.min(angleDiff, 360 - angleDiff)

        // Only draw arrow if aligned (within 60 degrees)
        if (normalizedAngleDiff > 60) return

        // Draw arrow from source to target
        const points = [
          [sourceStation.latitude, sourceStation.longitude],
          [targetStation.latitude, targetStation.longitude]
        ]

        // Arrow styling
        const windSpeed = sourceWind.wind_speed || 3
        const sourceColor = getAQIColor(sourceAQI.aqi || 100)
        const weight = Math.max(1, Math.min(5, windSpeed / 2))

        // Create polyline with arrow
        const polyline = L.polyline(points, {
          color: sourceColor,
          weight: weight,
          opacity: 0.6,
          dashArray: '5, 5',
          _windArrow: true
        }).addTo(map)

        // Add arrow marker at midpoint
        const midLat = (sourceStation.latitude + targetStation.latitude) / 2
        const midLon = (sourceStation.longitude + targetStation.longitude) / 2

        const arrowMarker = L.divIcon({
          html: `<div style="
            width: 20px;
            height: 20px;
            background-color: ${sourceColor};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            opacity: 0.8;
            transform: rotate(${calculateBearing(sourceStation.latitude, sourceStation.longitude, targetStation.latitude, targetStation.longitude)}deg);
          ">→</div>`,
          className: 'wind-arrow',
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        })

        L.marker([midLat, midLon], { icon: arrowMarker })
          .bindPopup(`
            <div style="font-size: 12px;">
              <strong>${sourceStation.name} → ${targetStation.name}</strong><br/>
              Wind: ${(sourceWind.wind_speed || 0).toFixed(1)} m/s from ${sourceWind.wind_direction || 0}°<br/>
              Source AQI: ${(sourceAQI.aqi || 100).toFixed(0)} (${sourceAQI.aqi_level || 'Moderate'})
            </div>
          `)
          .addTo(map)
          ._windArrow = true
      })
    })

  }, [map, stations, stationAQI, windData])

  return null
}

/**
 * Calculate bearing between two points
 * Returns degrees (0-360) where 0 = North, 90 = East, etc.
 */
function calculateBearing(lat1, lon1, lat2, lon2) {
  const dLon = lon2 - lon1
  const y = Math.sin(dLon) * Math.cos(lat2 * Math.PI / 180)
  const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
            Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLon)
  const bearing = Math.atan2(y, x) * 180 / Math.PI
  return (bearing + 360) % 360
}

export default WindVisualization
