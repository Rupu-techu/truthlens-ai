import { useEffect, useMemo, useState } from 'react'

import type { PredictionHistoryItem } from '../types/prediction'

const STORAGE_KEY = 'truthlens-ai.prediction-history'

function readStoredHistory(): PredictionHistoryItem[] {
  if (typeof window === 'undefined') {
    return []
  }

  try {
    const rawHistory = window.localStorage.getItem(STORAGE_KEY)
    if (!rawHistory) {
      return []
    }

    const parsedHistory: unknown = JSON.parse(rawHistory)
    if (!Array.isArray(parsedHistory)) {
      return []
    }

    return parsedHistory.filter((item): item is PredictionHistoryItem => {
      return (
        typeof item === 'object' &&
        item !== null &&
        typeof (item as PredictionHistoryItem).id === 'string' &&
        typeof (item as PredictionHistoryItem).text === 'string' &&
        typeof (item as PredictionHistoryItem).prediction === 'string' &&
        typeof (item as PredictionHistoryItem).confidence === 'number' &&
        typeof (item as PredictionHistoryItem).createdAt === 'string'
      )
    })
  } catch {
    return []
  }
}

// usePredictionHistory keeps the dashboard in sync with locally saved analysis history.
export function usePredictionHistory() {
  const [history, setHistory] = useState<PredictionHistoryItem[]>([])
  const [hasHydrated, setHasHydrated] = useState(false)

  useEffect(() => {
    setHistory(readStoredHistory())
    setHasHydrated(true)
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined' || !hasHydrated) {
      return
    }

    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
  }, [hasHydrated, history])

  const stats = useMemo(() => {
    const total = history.length
    const fakeCount = history.filter(
      (item) => item.prediction.trim().toLowerCase() === 'fake',
    ).length
    const realCount = history.filter(
      (item) => item.prediction.trim().toLowerCase() === 'real',
    ).length
    const averageConfidence =
      total === 0
        ? 0
        : history.reduce((sum, item) => sum + item.confidence, 0) / total

    return {
      total,
      fakeCount,
      realCount,
      averageConfidence,
      fakeRate: total === 0 ? 0 : (fakeCount / total) * 100,
    }
  }, [history])

  function addPrediction(item: PredictionHistoryItem): void {
    setHistory((currentHistory) => [item, ...currentHistory].slice(0, 20))
  }

  function clearHistory(): void {
    setHistory([])
  }

  return {
    history,
    stats,
    addPrediction,
    clearHistory,
  }
}
