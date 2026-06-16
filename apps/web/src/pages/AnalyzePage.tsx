import { useState } from 'react'

import PredictionForm from '../components/PredictionForm'
import PredictionResult from '../components/PredictionResult'
import SectionHeading from '../components/SectionHeading'
import { usePredictionHistory } from '../hooks/usePredictionHistory'
import type { PredictionResponse } from '../types/prediction'

function createHistoryId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `truthlens-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

// AnalyzePage is the core product surface where users submit article text and receive a verdict.
function AnalyzePage() {
  const [latestResult, setLatestResult] = useState<PredictionResponse | null>(null)
  const { addPrediction } = usePredictionHistory()

  return (
    <div className="mx-auto w-full max-w-7xl space-y-10 px-4 py-10 sm:px-6 lg:px-8">
      <SectionHeading
        eyebrow="Analyze"
        title="Paste any article and let TruthLens AI evaluate it"
        description="The interface is intentionally spacious and calm so the result feels like a polished product experience."
      />

      <div className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <PredictionForm
          onResult={(result) => {
            setLatestResult(result)
          }}
          onAnalyze={({ text, result }) => {
            addPrediction({
              id: createHistoryId(),
              text,
              prediction: result.prediction,
              confidence: result.confidence,
              createdAt: new Date().toISOString(),
            })
          }}
        />

        <div className="space-y-6">
          {latestResult ? (
            <PredictionResult
              prediction={latestResult.prediction}
              confidence={latestResult.confidence}
            />
          ) : (
            <div className="rounded-2xl border border-stone-200 bg-white p-8 shadow-[0_24px_80px_rgba(107,70,193,0.08)]">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
                Result Area
              </p>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
                Your prediction will appear here
              </h2>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                After analysis, the card will show whether the article is Fake News or Real News, along with a confidence score and progress bar.
              </p>

              <div className="mt-6 rounded-2xl bg-stone-50 p-4 text-sm text-slate-500">
                Prediction:
                <span className="ml-2 font-semibold text-slate-800">Pending</span>
                <br />
                Confidence:
                <span className="ml-2 font-semibold text-slate-800">--%</span>
              </div>
            </div>
          )}

          <div className="rounded-2xl border border-stone-200 bg-[linear-gradient(135deg,_#faf5ff_0%,_#ffffff_55%,_#fdf2f8_100%)] p-6 shadow-sm">
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
              Input Area
            </p>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              Use this page to test real articles, classroom examples, or synthetic content when demonstrating the model.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyzePage
