/**
 * AQI color utilities and constants
 */

export const AQI_CATEGORIES = {
  GOOD: { min: 0, max: 50, label: 'Good', color: '#4CAF50', bgColor: '#E8F5E9', textColor: '#1B5E20' },
  MODERATE: { min: 51, max: 100, label: 'Moderate', color: '#FFC107', bgColor: '#FFF3E0', textColor: '#E65100' },
  UNHEALTHY_SENSITIVE: { min: 101, max: 150, label: 'Unhealthy for Sensitive Groups', color: '#FF9800', bgColor: '#FFE0B2', textColor: '#E65100' },
  UNHEALTHY: { min: 151, max: 200, label: 'Unhealthy', color: '#F44336', bgColor: '#FFEBEE', textColor: '#B71C1C' },
  VERY_UNHEALTHY: { min: 200, max: 300, label: 'Very Unhealthy', color: '#9C27B0', bgColor: '#F3E5F5', textColor: '#4A148C' },
  HAZARDOUS: { min: 300, max: Infinity, label: 'Hazardous', color: '#5D0A0A', bgColor: '#8B0000', textColor: '#FFE0E0' }
}

export const getAQICategory = (aqi) => {
  if (aqi <= 50) return AQI_CATEGORIES.GOOD
  if (aqi <= 100) return AQI_CATEGORIES.MODERATE
  if (aqi <= 150) return AQI_CATEGORIES.UNHEALTHY_SENSITIVE
  if (aqi <= 200) return AQI_CATEGORIES.UNHEALTHY
  if (aqi <= 300) return AQI_CATEGORIES.VERY_UNHEALTHY
  return AQI_CATEGORIES.HAZARDOUS
}

export const getAQIColor = (aqi) => {
  return getAQICategory(aqi).color
}

export const getAQIBgColor = (aqi) => {
  return getAQICategory(aqi).bgColor
}

export const getAQITextColor = (aqi) => {
  return getAQICategory(aqi).textColor
}

export const getAQILabel = (aqi) => {
  return getAQICategory(aqi).label
}

/**
 * Get wind direction sector (N, NE, E, etc.)
 */
export const getWindSector = (degrees) => {
  const sectors = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
  const index = Math.round((degrees + 11.25) / 22.5) % 16
  return sectors[index]
}

/**
 * Get wind speed description
 */
export const getWindSpeedDescription = (windSpeed) => {
  if (windSpeed < 1) return 'Calm'
  if (windSpeed < 3) return 'Light'
  if (windSpeed < 8) return 'Moderate'
  if (windSpeed < 14) return 'Fresh'
  if (windSpeed < 17) return 'Strong'
  return 'Gale'
}
