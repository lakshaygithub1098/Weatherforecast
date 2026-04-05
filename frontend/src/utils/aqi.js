/**
 * Utility functions for AQI calculations and display
 */

/**
 * Get AQI category based on value
 */
export const getAQICategory = (aqi) => {
  if (aqi <= 50) return { label: 'Good', category: 'good' }
  if (aqi <= 100) return { label: 'Fair', category: 'fair' }
  if (aqi <= 200) return { label: 'Moderate', category: 'moderate' }
  if (aqi <= 300) return { label: 'Poor', category: 'poor' }
  if (aqi <= 400) return { label: 'Very Poor', category: 'very-poor' }
  return { label: 'Severe', category: 'severe' }
}

/**
 * Get color for AQI value (for map markers)
 */
export const getAQIColor = (aqi) => {
  if (aqi <= 50) return '#2ecc71'      // Green
  if (aqi <= 100) return '#f1c40f'     // Yellow
  if (aqi <= 200) return '#e67e22'     // Orange
  if (aqi <= 300) return '#e74c3c'     // Red
  if (aqi <= 400) return '#8b0000'     // Dark red
  return '#4b0000'                      // Very dark red
}

/**
 * Get wind direction label from degrees
 */
export const getWindDirection = (degrees) => {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
  const index = Math.round(degrees / 22.5) % 16
  return directions[index]
}

/**
 * Convert wind direction degrees to human-readable format
 */
export const formatWindDirection = (degrees) => {
  return `${getWindDirection(degrees)} (${Math.round(degrees)}°)`
}

/**
 * Format prediction data for display
 */
export const formatPrediction = (data) => {
  if (!data) return null
  
  const { aqi, xgboost_prediction, lstm_prediction, model_confidence } = data
  
  return {
    aqi: aqi.toFixed(1),
    xgbPred: xgboost_prediction.toFixed(1),
    lstmPred: lstm_prediction.toFixed(1),
    xgbConfidence: (model_confidence.xgboost * 100).toFixed(0),
    lstmConfidence: (model_confidence.lstm * 100).toFixed(0),
  }
}

/**
 * Get health recommendation based on AQI
 */
export const getHealthRecommendation = (aqi) => {
  if (aqi <= 50) return 'Air quality is satisfactory. Outdoor activities recommended.'
  if (aqi <= 100) return 'Air quality is acceptable. Sensitive groups may experience issues.'
  if (aqi <= 200) return 'Members of sensitive groups may experience health issues. Consider limiting outdoor exposure.'
  if (aqi <= 300) return 'General public may begin to experience health effects. Limit outdoor activities.'
  if (aqi <= 400) return 'Health alert. All groups will be affected. Avoid outdoor activities.'
  return 'Health warning. Stay indoors and keep activity levels low. Use air purifiers.'
}

/**
 * Create drag icon for map
 */
export const createDragIcon = () => {
  const svgString = `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="1"></circle>
      <circle cx="12" cy="5" r="1"></circle>
      <circle cx="12" cy="19" r="1"></circle>
      <circle cx="5" cy="12" r="1"></circle>
      <circle cx="19" cy="12" r="1"></circle>
    </svg>
  `
  return `data:image/svg+xml;base64,${btoa(svgString)}`
}
