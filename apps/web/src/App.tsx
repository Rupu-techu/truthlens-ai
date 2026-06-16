import { useState } from 'react'

import PredictionForm from './components/PredictionForm'
import PredictionResult from './components/PredictionResult'
import type { PredictionResponse } from './services/predictionService'

function App() {
  const [result, setResult] = useState<PredictionResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState('')

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_35%),linear-gradient(180deg,_#020617_0%,_#0f172a_45%,_#020617_100%)] text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-8 sm:px-8 lg:px-10">
        <header className="flex items-center justify-between border-b border-white/10 pb-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-cyan-300">
              TruthLens AI
            </p>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
              Fast, modern fake news detection powered by a trained TF-IDF and Logistic Regression pipeline.
            </p>
          </div>

          <div className="hidden rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs font-medium text-cyan-200 md:block">
            Real-time analysis
          </div>
        </header>

        <section className="grid flex-1 items-center gap-10 py-10 lg:grid-cols-[1.05fr_0.95fr] lg:gap-14">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">
              <span className="h-2 w-2 rounded-full bg-cyan-400" />
              AI-assisted truth verification
            </div>

            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
              TruthLens AI
            </h1>

            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
              Paste a news article, analyze it instantly, and get a clear Fake or Real prediction with confidence scoring.
              Built for a clean, focused fact-checking workflow.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-medium text-white">Paste text</p>
                <p className="mt-1 text-sm leading-6 text-slate-400">
                  Drop in the full article or news story.
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-medium text-white">Analyze</p>
                <p className="mt-1 text-sm leading-6 text-slate-400">
                  Call the FastAPI backend for a prediction.
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-medium text-white">Review result</p>
                <p className="mt-1 text-sm leading-6 text-slate-400">
                  See the confidence score and verdict immediately.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <PredictionForm
              onResult={(predictionResult) => {
                setResult(predictionResult)
                setErrorMessage('')
              }}
              onError={(message) => {
                setErrorMessage(message)
                setResult(null)
              }}
            />

            {errorMessage ? (
              <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                {errorMessage}
              </div>
            ) : null}

            {result ? (
              <PredictionResult
                prediction={result.prediction}
                confidence={result.confidence}
              />
            ) : (
              <div className="rounded-xl border border-dashed border-white/15 bg-white/5 p-6 text-sm leading-6 text-slate-400">
                Your prediction result will appear here after analysis.
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
