import SectionHeading from '../components/SectionHeading'

const techStack = [
  'React',
  'TypeScript',
  'Vite',
  'Tailwind CSS',
  'React Router',
  'FastAPI',
  'scikit-learn',
  'TF-IDF',
  'Logistic Regression',
  'Joblib',
]

// AboutPage explains the project, dataset, ML approach, and author context.
function AboutPage() {
  return (
    <div className="mx-auto w-full max-w-7xl space-y-10 px-4 py-10 sm:px-6 lg:px-8">
      <SectionHeading
        eyebrow="About"
        title="A portfolio-ready AI product for fake news detection"
        description="TruthLens AI pairs a polished interface with a practical binary text classification pipeline, making it a strong engineering internship showcase."
      />

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
            Project Overview
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
            Built to make credibility checks fast, understandable, and demo-friendly
          </h2>
          <p className="mt-4 text-sm leading-7 text-slate-600">
            TruthLens AI is a compact end-to-end product that lets a user paste a news article, analyze it in the browser, and receive a structured prediction from a trained FastAPI backend.
          </p>
          <p className="mt-4 text-sm leading-7 text-slate-600">
            The UI uses warm white surfaces, soft gray borders, and lavender accents to feel more like a modern product portfolio piece than a classroom prototype.
          </p>
        </section>

        <aside className="rounded-2xl border border-stone-200 bg-[linear-gradient(135deg,_#faf5ff_0%,_#ffffff_60%,_#fff7fb_100%)] p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
            Author
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
            Rupsha Debnath
          </h2>
          <p className="mt-4 text-sm leading-7 text-slate-600">
            Engineering internship project focused on full-stack AI delivery, clean UX, and practical machine learning deployment.
          </p>
        </aside>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
            Dataset Information
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
            Trained on labeled news articles
          </h2>
          <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-600">
            <li>• Source files used during training: <span className="font-medium text-slate-900">Fake.csv</span> and <span className="font-medium text-slate-900">True.csv</span>.</li>
            <li>• After deduplication, the dataset contained roughly <span className="font-medium text-slate-900">23,478 fake</span> and <span className="font-medium text-slate-900">21,211 real</span> articles.</li>
            <li>• The notebooks combined title and text into a single content field for classification.</li>
            <li>• The task is binary classification: predict whether a news item is <span className="font-medium text-slate-900">Fake</span> or <span className="font-medium text-slate-900">Real</span>.</li>
          </ul>
        </section>

        <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
            ML Model Details
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
            Simple, explainable, and fast
          </h2>
          <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-600">
            <li>• Text is transformed using a <span className="font-medium text-slate-900">TF-IDF vectorizer</span>.</li>
            <li>• The classifier is a <span className="font-medium text-slate-900">Logistic Regression</span> model.</li>
            <li>• Model artifacts are loaded with <span className="font-medium text-slate-900">Joblib</span> on FastAPI startup.</li>
            <li>• The frontend renders the result as a confidence-driven UX component.</li>
          </ul>
        </section>
      </div>

      <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-[0_18px_50px_rgba(107,70,193,0.06)]">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-violet-500">
          Tech Stack
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          {techStack.map((item) => (
            <span
              key={item}
              className="rounded-full border border-violet-200 bg-violet-50 px-4 py-2 text-sm font-medium text-violet-700"
            >
              {item}
            </span>
          ))}
        </div>
      </section>
    </div>
  )
}

export default AboutPage
