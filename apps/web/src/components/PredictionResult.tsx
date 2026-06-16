interface PredictionResultProps {
  prediction: string
  confidence: number
}

// Renders a verdict card with a red warning state for fake news and a green success state for real news.
function WarningIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-5 w-5"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-5 w-5"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20 6 9 17l-5-5" />
      <path d="M21 12a9 9 0 1 1-9-9" />
    </svg>
  )
}

function PredictionResult({ prediction, confidence }: PredictionResultProps) {
  const normalizedPrediction = prediction.trim().toLowerCase()
  const isFake = normalizedPrediction === 'fake'
  const isReal = normalizedPrediction === 'real'
  const safeConfidence = Math.max(0, Math.min(confidence, 100))
  const displayLabel = isFake ? 'Fake News' : isReal ? 'Real News' : prediction

  const themeClasses = isFake
    ? {
        container:
          'border-rose-500/30 bg-rose-500/10 text-rose-50 shadow-rose-950/20',
        badge: 'bg-rose-500/15 text-rose-100 ring-1 ring-rose-400/30',
        progress: 'bg-rose-400',
        track: 'bg-rose-500/15',
      }
    : {
        container:
          'border-emerald-500/30 bg-emerald-500/10 text-emerald-50 shadow-emerald-950/20',
        badge: 'bg-emerald-500/15 text-emerald-100 ring-1 ring-emerald-400/30',
        progress: 'bg-emerald-400',
        track: 'bg-emerald-500/15',
      }

  const Icon = isFake ? WarningIcon : CheckIcon

  return (
    <section
      className={`w-full rounded-xl border p-5 shadow-2xl backdrop-blur sm:p-6 ${themeClasses.container}`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <div className={`mt-0.5 rounded-full p-2 ${themeClasses.badge}`}>
            <Icon />
          </div>

          <div>
            <p className="text-sm font-medium uppercase tracking-[0.28em] text-white/70">
              Prediction
            </p>
            <h3 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
              {displayLabel}
            </h3>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-slate-950/20 px-4 py-3 text-left sm:text-right">
          <p className="text-sm uppercase tracking-[0.24em] text-white/70">
            Confidence
          </p>
          <p className="mt-1 text-2xl font-semibold">{safeConfidence.toFixed(2)}%</p>
        </div>
      </div>

      <div className="mt-6 space-y-2">
        <div className="flex items-center justify-between text-sm text-white/80">
          <span>Confidence score</span>
          <span>{safeConfidence.toFixed(0)} / 100</span>
        </div>

        <div className={`h-3 overflow-hidden rounded-full ${themeClasses.track}`}>
          <div
            className={`h-full rounded-full transition-all duration-500 ${themeClasses.progress}`}
            style={{ width: `${safeConfidence}%` }}
            aria-hidden="true"
          />
        </div>
      </div>

      {!isFake && !isReal ? (
        <p className="mt-4 text-sm text-white/70">
          The model returned a custom label. Showing the raw result while keeping the confidence display.
        </p>
      ) : null}
    </section>
  )
}

export default PredictionResult
