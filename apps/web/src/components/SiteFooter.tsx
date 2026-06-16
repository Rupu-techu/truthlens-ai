// SiteFooter keeps the product identity present without adding visual noise.
function SiteFooter() {
  return (
    <footer className="border-t border-stone-200/80">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-3 px-4 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <p>TruthLens AI · Engineering internship project</p>
        <p>Built with React, TypeScript, Tailwind CSS, and FastAPI.</p>
      </div>
    </footer>
  )
}

export default SiteFooter
