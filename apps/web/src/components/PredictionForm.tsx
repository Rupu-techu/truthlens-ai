import { useState } from 'react'
import type { FormEvent } from 'react'

import {
  predictNews,
  PredictionServiceError,
} from '../services/predictionService'
import type { PredictionResponse } from '../types/prediction'

interface PredictionFormProps {
  onResult: (result: PredictionResponse) => void
  onAnalyze?: (payload: { text: string; result: PredictionResponse }) => void
  onError?: (message: string) => void
}

const MIN_TEXT_LENGTH = 20

function getValidationMessage(text: string): string {
  const trimmedText = text.trim()

  if (!trimmedText) {
    return 'Please paste an article or news text.'
  }

  if (trimmedText.length < MIN_TEXT_LENGTH) {
    return `Please enter at least ${MIN_TEXT_LENGTH} characters.`
  }

  return ''
}

// PredictionForm collects article text, validates it, and triggers the backend request.
function PredictionForm({ onResult, onAnalyze, onError }: PredictionFormProps) {
  const [text, setText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const characterCount = text.trim().length

  const remainingCharacters = Math.max(MIN_TEXT_LENGTH - characterCount, 0)

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()

    const validationMessage = getValidationMessage(text)
    if (validationMessage) {
      setErrorMessage(validationMessage)
      onError?.(validationMessage)
      return
    }

    setIsSubmitting(true)
    setErrorMessage('')

    try {
      const cleanedText = text.trim()
      const result = await predictNews(cleanedText)
      onResult(result)
      onAnalyze?.({ text: cleanedText, result })
    } catch (error: unknown) {
      const message =
        error instanceof PredictionServiceError
          ? error.message
          : 'Unable to analyze the text right now.'

      setErrorMessage(message)
      onError?.(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="w-full rounded-2xl border border-stone-200 bg-white p-5 shadow-[0_24px_80px_rgba(107,70,193,0.08)] sm:p-6 lg:p-8">
      <div className="mb-6">
        <p className="text-sm font-medium uppercase tracking-[0.28em] text-violet-500">
          TruthLens AI
        </p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
          Paste a news article to analyze it
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
          Drop in the article text below and the model will classify it as Fake
          or Real with a confidence score.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label
            htmlFor="prediction-text"
            className="text-sm font-medium text-slate-700"
          >
            Article text
          </label>
          <textarea
            id="prediction-text"
            name="prediction-text"
            value={text}
            onChange={(event) => {
              setText(event.target.value)
              if (errorMessage) {
                setErrorMessage('')
              }
            }}
            placeholder="Paste the full article or news story here..."
            className="min-h-64 w-full resize-y rounded-2xl border border-stone-200 bg-stone-50 px-4 py-4 text-base leading-7 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-300 focus:bg-white focus:ring-4 focus:ring-violet-100 sm:min-h-72"
          />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-slate-500">
            <span className={characterCount < MIN_TEXT_LENGTH ? 'text-amber-600' : 'text-emerald-600'}>
              {characterCount}
            </span>
            <span className="mx-1">characters</span>
            <span className="text-slate-300">|</span>
            <span className="ml-1">
              {remainingCharacters > 0
                ? `${remainingCharacters} more to reach the minimum`
                : 'Minimum length met'}
            </span>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-400 px-5 py-3 text-sm font-semibold text-white transition duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-violet-200 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? 'Analyzing...' : 'Analyze Article'}
          </button>
        </div>

        {errorMessage ? (
          <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {errorMessage}
          </p>
        ) : null}
      </form>
    </section>
  )
}

export default PredictionForm
