import { FormEvent, useState } from 'react'

import {
  predictNews,
  type PredictionResponse,
  PredictionServiceError,
} from '../services/predictionService'

interface PredictionFormProps {
  onResult: (result: PredictionResponse) => void
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

function PredictionForm({ onResult, onError }: PredictionFormProps) {
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
      const result = await predictNews(text)
      onResult(result)
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
    <section className="w-full rounded-xl border border-slate-800/80 bg-slate-950/80 p-5 shadow-2xl shadow-cyan-950/20 backdrop-blur sm:p-6 lg:p-8">
      <div className="mb-6">
        <p className="text-sm font-medium uppercase tracking-[0.28em] text-cyan-300">
          TruthLens AI
        </p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-50 sm:text-3xl">
          Paste a news article to analyze it
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
          Drop in the article text below and the model will classify it as Fake
          or Real with a confidence score.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label
            htmlFor="prediction-text"
            className="text-sm font-medium text-slate-200"
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
            className="min-h-56 w-full resize-y rounded-xl border border-slate-700 bg-slate-900/90 px-4 py-4 text-base leading-7 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/30 sm:min-h-64"
          />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-slate-400">
            <span className={characterCount < MIN_TEXT_LENGTH ? 'text-amber-300' : 'text-emerald-300'}>
              {characterCount}
            </span>
            <span className="mx-1">characters</span>
            <span className="text-slate-500">|</span>
            <span className="ml-1">
              {remainingCharacters > 0
                ? `${remainingCharacters} more to reach the minimum`
                : 'Minimum length met'}
            </span>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:from-cyan-300 hover:to-blue-400 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {errorMessage ? (
          <p className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {errorMessage}
          </p>
        ) : null}
      </form>
    </section>
  )
}

export default PredictionForm
