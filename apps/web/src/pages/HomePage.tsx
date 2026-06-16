import { Link } from 'react-router-dom'

import SectionHeading from '../components/SectionHeading'

const features = [
  {
    title: 'Instant AI Verdicts',
    description:
      'Paste news text and get an immediate Fake or Real prediction backed by a trained TF-IDF and Logistic Regression pipeline.',
  },
  {
    title: 'Built for Students',
    description:
      'Designed as an engineering internship project with a clean, credible interface that feels polished in presentations.',
  },
  {
    title: 'Portfolio-Ready UI',
    description:
      'Minimal, premium, and responsive with subtle gradients, rounded-2xl cards, and soft lavender accents.',
  },
]

const steps = [
  {
    number: '01',
    title: 'Paste article text',
    description:
      'Copy any article or news story into the analyze page input area.',
  },
  {
    number: '02',
    title: 'Run the model',
    description:
      'The frontend calls the FastAPI backend and sends the text to the trained classifier.',
  },
  {
    number: '03',
    title: 'Review the result',
    description:
      'See the prediction, confidence score, and a visual confidence bar in a polished result card.',
  },
]

// HomePage is the marketing-style landing page that introduces the product.
function HomePage() {
  return (
    <div className="space-y-24 py-8">
      <section className="mx-auto grid w-full max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:px-8">
        <div className="flex flex-col justify-center">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-violet-200 bg-white px-4 py-2 text-sm text-slate-600 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-violet-500" />
            AI-Powered Fake News Detection for Students
          </div>

          <h1 className="mt-8 max-w-3xl text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
            Detect Fake News in Seconds.
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl">
            TruthLens AI turns a long article into a clear, evidence-style verdict with a modern interface
            inspired by Linear, Notion, and Vercel.
          </p>

          <div className="mt-10 flex flex-col gap-3 sm:flex-row">
            <Link
              to="/analyze"
              className="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-400 px-6 py-3.5 text-sm font-semibold text-white transition duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-violet-200"
            >
              Start Analyzing
            </Link>
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center rounded-2xl border border-stone-200 bg-white px-6 py-3.5 text-sm font-semibold text-slate-700 transition duration-300 hover:-translate-y-0.5 hover:border-violet-200 hover:shadow-md"
            >
              View Dashboard
            </Link>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-3">
            {[
              { label: 'Model', value: 'TF-IDF + Logistic Regression' },
              { label: 'Focus', value: 'Student-friendly fact checking' },
              { label: 'Style', value: 'Minimal premium AI SaaS' },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-stone-200 bg-white/80 p-4 shadow-sm backdrop-blur"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">
                  {item.label}
                </p>
                <p className="mt-2 text-sm font-medium text-slate-800">{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 -z-10 rounded-[2rem] bg-[radial-gradient(circle_at_top_right,_rgba(167,139,250,0.22),_transparent_55%),radial-gradient(circle_at_bottom_left,_rgba(244,114,182,0.16),_transparent_45%)] blur-3xl" />
          <div className="rounded-[2rem] border border-stone-200 bg-white p-6 shadow-[0_30px_100px_rgba(107,70,193,0.12)]">
            <div className="rounded-[1.5rem] bg-[linear-gradient(180deg,_#faf7ff_0%,_#ffffff_100%)] p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.32em] text-violet-500">
                Preview
              </p>
              <div className="mt-5 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                <p className="text-sm font-semibold text-slate-500">Prediction</p>
                <div className="mt-3 flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-rose-50 text-xl">
                    🟥
                  </span>
                  <div>
                    <p className="text-2xl font-semibold text-slate-900">Fake News</p>
                    <p className="text-sm text-slate-500">High confidence classification</p>
                  </div>
                </div>
                <div className="mt-5 space-y-2">
                  <div className="flex items-center justify-between text-sm text-slate-500">
                    <span>Confidence</span>
                    <span>90.59%</span>
                  </div>
                  <div className="h-3 rounded-full bg-stone-100">
                    <div className="h-full w-[90.59%] rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="Features"
          title="A focused AI product experience"
          description="TruthLens AI is designed to feel like a real product showcase: refined, credible, and structured for a strong internship portfolio."
        />

        <div className="mt-10 grid gap-5 lg:grid-cols-3">
          {features.map((feature, index) => (
            <article
              key={feature.title}
              className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-lg"
            >
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-violet-500">
                0{index + 1}
              </p>
              <h3 className="mt-4 text-xl font-semibold text-slate-900">
                {feature.title}
              </h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                {feature.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="How It Works"
          title="From article to verdict in three simple steps"
          description="A clean, transparent flow keeps the experience easy to demo during interviews or classroom presentations."
        />

        <div className="mt-10 grid gap-5 lg:grid-cols-3">
          {steps.map((step) => (
            <article
              key={step.number}
              className="rounded-2xl border border-stone-200 bg-stone-50 p-6 shadow-sm"
            >
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-violet-500">
                {step.number}
              </p>
              <h3 className="mt-4 text-xl font-semibold text-slate-900">
                {step.title}
              </h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                {step.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 pb-10 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] border border-violet-200 bg-[linear-gradient(135deg,_#f8f3ff_0%,_#ffffff_45%,_#fff7fc_100%)] p-8 shadow-[0_24px_80px_rgba(107,70,193,0.12)] sm:p-10">
          <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
                Call To Action
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
                Ready to test TruthLens AI?
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
                Move to the analyze page and paste a news article to see the prediction engine, confidence
                visualization, and local history flow in action.
              </p>
            </div>

            <Link
              to="/analyze"
              className="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-6 py-3.5 text-sm font-semibold text-white transition duration-300 hover:-translate-y-0.5 hover:bg-slate-800"
            >
              Analyze an Article
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
