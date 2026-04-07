import React, { useMemo } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

/**
 * Forecast with Confidence Bands Component
 * Displays 24-hour AQI forecast with uncertainty bands based on model RMSE
 * 
 * Props:
 * - forecast: Array of {hour, aqi, upwind_influence}
 * - rmse: Root Mean Square Error of model (±confidence band width)
 * - title: Chart title (e.g., "NSUT 24-Hour Forecast")
 */
export const ForecastConfidenceBands = ({ forecast, rmse = 18, title = '24-Hour AQI Forecast' }) => {
  const data = useMemo(() => {
    if (!forecast || !Array.isArray(forecast)) return []

    return forecast.map((item, index) => ({
      hour: item.hour || `Hour ${index}`,
      aqi: Math.round(item.aqi || 0),
      upper: Math.round((item.aqi || 0) + rmse),
      lower: Math.max(0, Math.round((item.aqi || 0) - rmse)),
      name: item.name || `H+${index}`
    }))
  }, [forecast, rmse])

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <p className="text-sm text-gray-600">
          Confidence Band: ±{rmse} AQI (Model RMSE)
        </p>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <defs>
            {/* Lower uncertainty band gradient */}
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1} />
            </linearGradient>

            {/* Forecast line gradient (color changes by severity) */}
            <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
              <stop offset="50%" stopColor="#ffc658" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ff7c7c" stopOpacity={0.8} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="hour"
            stroke="#666"
            style={{ fontSize: '12px' }}
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            stroke="#666"
            label={{ value: 'AQI', angle: -90, position: 'insideLeftBottom', offset: 10 }}
            style={{ fontSize: '12px' }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '4px',
              padding: '8px'
            }}
            formatter={(value, name) => {
              if (name === 'aqi') return [value, 'Forecast']
              if (name === 'upper') return [value, 'Upper Band (+RMSE)']
              if (name === 'lower') return [value, 'Lower Band (-RMSE)']
              return [value, name]
            }}
            labelFormatter={(label) => `${label}`}
          />

          {/* Upper uncertainty band */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="#bbb"
            opacity={0.15}
            name="Upper Confidence"
            isAnimationActive={false}
          />

          {/* Lower uncertainty band */}
          <Area
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="#bbb"
            opacity={0.15}
            name="Lower Confidence"
            isAnimationActive={false}
          />

          {/* Main forecast line with gradient */}
          <Area
            type="monotone"
            dataKey="aqi"
            stroke="#ff7c7c"
            fill="url(#forecastGradient)"
            strokeWidth={2}
            dot={{ fill: '#ff7c7c', r: 4 }}
            activeDot={{ r: 6 }}
            name="AQI Forecast"
            isAnimationActive={true}
          />

          <Legend />
        </AreaChart>
      </ResponsiveContainer>

      {/* Statistics Footer */}
      <div className="mt-4 grid grid-cols-4 gap-4 text-center text-sm">
        <div className="bg-gray-50 p-3 rounded">
          <p className="text-gray-600">Min</p>
          <p className="font-bold text-gray-800">
            {data.length > 0 ? Math.min(...data.map(d => d.aqi)) : '-'}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <p className="text-gray-600">Max</p>
          <p className="font-bold text-gray-800">
            {data.length > 0 ? Math.max(...data.map(d => d.aqi)) : '-'}
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <p className="text-gray-600">Avg</p>
          <p className="font-bold text-gray-800">
            {data.length > 0 ? Math.round(data.reduce((sum, d) => sum + d.aqi, 0) / data.length) : '-'}
          </p>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-gray-600">RMSE Margin</p>
          <p className="font-bold text-blue-600">±{rmse}</p>
        </div>
      </div>
    </div>
  )
}

export default ForecastConfidenceBands
