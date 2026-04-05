import React from 'react'
import { motion } from 'framer-motion'

/**
 * Loading Spinner Component
 */
export const LoadingSpinner = ({ text = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center space-y-4 py-8">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full"
      />
      <p className="text-gray-500 text-sm">{text}</p>
    </div>
  )
}

/**
 * Error Alert Component
 */
export const ErrorAlert = ({ message, onDismiss }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 flex items-start justify-between gap-4"
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">⚠️</span>
        <div>
          <h3 className="font-semibold text-red-800">Error</h3>
          <p className="text-red-700 text-sm mt-1">{message}</p>
        </div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-500 hover:text-red-700 text-xl leading-none"
        >
          ✕
        </button>
      )}
    </motion.div>
  )
}

/**
 * Success Toast Component
 */
export const SuccessToast = ({ message }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
      className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3"
    >
      <span className="text-2xl">✓</span>
      <p className="text-green-700 text-sm">{message}</p>
    </motion.div>
  )
}

/**
 * Empty State Component
 */
export const EmptyState = ({ icon = '📍', title, description }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-500 text-sm max-w-md">{description}</p>
    </div>
  )
}

/**
 * Skeleton Loader Component
 */
export const SkeletonLoader = ({ lines = 3 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: lines }).map((_, i) => (
        <motion.div
          key={i}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="h-4 bg-gray-200 rounded"
        />
      ))}
    </div>
  )
}

export default {
  LoadingSpinner,
  ErrorAlert,
  SuccessToast,
  EmptyState,
  SkeletonLoader,
}
