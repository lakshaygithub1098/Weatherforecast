import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const predictionsAPI = {
  /**
   * Get AQI prediction for a location
   */
  predict: async (latitude, longitude, stationName = null) => {
    const response = await api.post('/predict', {
      latitude,
      longitude,
      station_name: stationName
    })
    return response.data
  },

  /**
   * Get list of monitoring stations
   */
  getStations: async () => {
    const response = await api.get('/stations')
    return response.data.stations
  },

  /**
   * Check API health
   */
  health: async () => {
    const response = await api.get('/health')
    return response.data
  },

  /**
   * Get model information
   */
  modelInfo: async () => {
    const response = await api.get('/models/info')
    return response.data
  },
}

export default api
