interface PredictionResultProps {
  prediction: string
  confidence: number
}

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

// PredictionResult translates the raw API response into a polished verdict card.
function PredictionResult({ prediction, confidence }: PredictionResultProps) {
  const normalizedPrediction = prediction.trim().toLowerCase()
  const isFake = normalizedPrediction === 'fake'
  const isReal = normalizedPrediction === 'real'
  const safeConfidence = Math.max(0, Math.min(confidence, 100))
  const displayLabel = isFake ? 'Fake News' : isReal ? 'Real News' : prediction

  const themeClasses = isFake
    ? {
        shell: 'border-rose-200 bg-rose-50 text-slate-900',
        badge: 'bg-rose-100 text-rose-700 ring-1 ring-rose-200',
        track: 'bg-rose-100',
        fill: 'bg-gradient-to-r from-rose-400 to-orange-300',
        icon: WarningIcon,
      }
    : isReal
      ? {
          shell: 'border-emerald-200 bg-emerald-50 text-slate-900',
          badge: 'bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200',
          track: 'bg-emerald-100',
          fill: 'bg-gradient-to-r from-emerald-400 to-lime-300',
          icon: CheckIcon,
        }
      : {
          shell: 'border-stone-200 bg-stone-50 text-slate-900',
          badge: 'bg-stone-100 text-slate-600 ring-1 ring-stone-200',
          track: 'bg-stone-100',
          fill: 'bg-gradient-to-r from-violet-400 to-fuchsia-300',
          icon: CheckIcon,
        }

  const Icon = themeClasses.icon

  return (
    <section className={`w-full rounded-2xl border p-5 shadow-[0_20px_60px_rgba(107,70,193,0.08)] sm:p-6 ${themeClasses.shell}`}>
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-4">
          <div className={`rounded-2xl p-3 ${themeClasses.badge}`}>
            <Icon />
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
              Prediction
            </p>
            <h3 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
              {displayLabel}
            </h3>
            <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
              The model has classified the submitted article and returned its confidence score below.
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-stone-200 bg-white px-4 py-3 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">
            Confidence
          </p>
          <p className="mt-1 text-3xl font-semibold tracking-tight">
            {safeConfidence.toFixed(2)}%
          </p>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        <div className="flex items-center justify-between text-sm text-slate-500">
          <span>Confidence visualization</span>
          <span>{safeConfidence.toFixed(0)} / 100</span>
        </div>

        <div className={`h-3 overflow-hidden rounded-full ${themeClasses.track}`}>
          <div
            className={`h-full rounded-full transition-all duration-500 ${themeClasses.fill}`}
            style={{ width: `${safeConfidence}%` }}
            aria-hidden="true"
          />
        </div>
      </div>
    </section>
  )
}

export default PredictionResult
