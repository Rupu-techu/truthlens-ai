import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Analyze', to: '/analyze' },
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'About', to: '/about' },
]

// SiteHeader renders the top navigation used across the entire product.
function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-stone-200/80 bg-[rgba(250,248,244,0.86)] backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <NavLink to="/" className="group inline-flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-purple-300 text-sm font-semibold text-white shadow-lg shadow-violet-200/50 transition duration-300 group-hover:scale-105">
            TL
          </span>
          <span>
            <span className="block text-sm font-semibold tracking-[0.24em] text-slate-500 uppercase">
              TruthLens AI
            </span>
            <span className="block text-xs text-slate-400">
              AI-Powered Fake News Detection
            </span>
          </span>
        </NavLink>

        <nav className="hidden items-center gap-2 md:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  'rounded-full px-4 py-2 text-sm font-medium transition duration-300',
                  isActive
                    ? 'bg-white text-slate-900 shadow-sm ring-1 ring-stone-200'
                    : 'text-slate-500 hover:bg-white hover:text-slate-900 hover:shadow-sm',
                ].join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}

export default SiteHeader
