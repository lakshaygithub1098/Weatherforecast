import { create } from 'zustand'

export const usePredictionStore = create((set) => ({
  predictions: {},
  selectedStation: null,
  loading: false,
  error: null,
  
  setPrediction: (stationId, data) =>
    set((state) => ({
      predictions: {
        ...state.predictions,
        [stationId]: data,
      },
    })),
  
  setSelectedStation: (stationId) =>
    set({ selectedStation: stationId }),
  
  setLoading: (loading) =>
    set({ loading }),
  
  setError: (error) =>
    set({ error }),
  
  clearError: () =>
    set({ error: null }),
  
  getPrediction: (stationId) =>
    get((state) => state.predictions[stationId]),
}))
