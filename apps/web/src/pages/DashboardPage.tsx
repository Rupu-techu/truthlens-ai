import { Link } from 'react-router-dom'

import SectionHeading from '../components/SectionHeading'
import { usePredictionHistory } from '../hooks/usePredictionHistory'

function formatShortDate(value: string): string {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

// DashboardPage summarizes local prediction history and makes the app feel data-rich.
function DashboardPage() {
  const { history, stats, clearHistory } = usePredictionHistory()

  const fakeShare = stats.total === 0 ? 0 : (stats.fakeCount / stats.total) * 100
  const realShare = stats.total === 0 ? 0 : (stats.realCount / stats.total) * 100

  return (
    <div className="mx-auto w-full max-w-7xl space-y-10 px-4 py-10 sm:px-6 lg:px-8">
      <SectionHeading
        eyebrow="Dashboard"
        title="Track your recent analyses and model performance"
        description="This dashboard uses local storage so you can preview a personalized analytics experience without needing a database."
      />

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {[
          {
            label: 'Total Predictions',
            value: stats.total,
            accent: 'from-violet-600 to-fuchsia-500',
          },
          {
            label: 'Fake News',
            value: stats.fakeCount,
            accent: 'from-rose-500 to-orange-400',
          },
          {
            label: 'Real News',
            value: stats.realCount,
            accent: 'from-emerald-500 to-lime-400',
          },
          {
            label: 'Average Confidence',
            value: `${stats.averageConfidence.toFixed(1)}%`,
            accent: 'from-slate-700 to-slate-500',
          },
        ].map((item) => (
          <article
            key={item.label}
            className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]"
          >
            <div className={`h-1.5 w-16 rounded-full bg-gradient-to-r ${item.accent}`} />
            <p className="mt-5 text-sm font-medium text-slate-500">{item.label}</p>
            <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
              {item.value}
            </p>
          </article>
        ))}
      </div>

      <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
            Fake vs Real Analytics
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
            Model output distribution
          </h2>

          <div className="mt-6 space-y-5">
            <div>
              <div className="mb-2 flex items-center justify-between text-sm text-slate-600">
                <span>Fake</span>
                <span>{fakeShare.toFixed(1)}%</span>
              </div>
              <div className="h-3 rounded-full bg-rose-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-rose-400 to-orange-300"
                  style={{ width: `${fakeShare}%` }}
                />
              </div>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between text-sm text-slate-600">
                <span>Real</span>
                <span>{realShare.toFixed(1)}%</span>
              </div>
              <div className="h-3 rounded-full bg-emerald-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-lime-300"
                  style={{ width: `${realShare}%` }}
                />
              </div>
            </div>
          </div>

          <p className="mt-6 text-sm leading-7 text-slate-600">
            The split is based on locally saved analyses, giving the dashboard a realistic product-demo feel.
          </p>
        </section>

        <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
                Recent Predictions
              </p>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
                Latest analysis results
              </h2>
            </div>

            {history.length > 0 ? (
              <button
                type="button"
                onClick={clearHistory}
                className="rounded-2xl border border-stone-200 bg-stone-50 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-violet-200 hover:bg-white"
              >
                Clear History
              </button>
            ) : null}
          </div>

          <div className="mt-6 space-y-4">
            {history.length > 0 ? (
              history.slice(0, 5).map((item) => {
                const isFake = item.prediction.trim().toLowerCase() === 'fake'
                return (
                  <article
                    key={item.id}
                    className="rounded-2xl border border-stone-200 bg-stone-50 p-4"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">
                          {isFake ? 'Fake News' : 'Real News'}
                        </p>
                        <p className="mt-1 line-clamp-2 text-sm leading-6 text-slate-600">
                          {item.text}
                        </p>
                      </div>

                      <div className="rounded-2xl bg-white px-3 py-2 text-right shadow-sm">
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                          Confidence
                        </p>
                        <p className="mt-1 text-lg font-semibold text-slate-900">
                          {item.confidence.toFixed(2)}%
                        </p>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                      <span>{formatShortDate(item.createdAt)}</span>
                      <span>{item.id.slice(0, 8)}</span>
                    </div>
                  </article>
                )
              })
            ) : (
              <div className="rounded-2xl border border-dashed border-stone-300 bg-stone-50 p-8 text-sm leading-7 text-slate-600">
                No local history yet. Run a prediction on the analyze page and your recent results will appear here.
              </div>
            )}
          </div>
        </section>
      </div>

      <div className="rounded-2xl border border-violet-200 bg-[linear-gradient(135deg,_#faf5ff_0%,_#ffffff_55%,_#fff7fb_100%)] p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
              Next Step
            </p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">
              Need a fresh prediction?
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
              Return to the analyze page, paste a new article, and watch the dashboard update automatically.
            </p>
          </div>

          <Link
            to="/analyze"
            className="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-6 py-3.5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
          >
            Analyze Another Article
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
