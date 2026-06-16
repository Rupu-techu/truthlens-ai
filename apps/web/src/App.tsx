import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import SiteFooter from './components/SiteFooter'
import SiteHeader from './components/SiteHeader'
import AboutPage from './pages/AboutPage'
import AnalyzePage from './pages/AnalyzePage'
import DashboardPage from './pages/DashboardPage'
import HomePage from './pages/HomePage'

// App defines the global shell and route structure for the frontend.
function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(196,181,253,0.28),_transparent_35%),linear-gradient(180deg,_#fbfaf7_0%,_#f5f1ff_100%)] text-slate-900">
        <SiteHeader />

        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <SiteFooter />
      </div>
    </BrowserRouter>
  )
}

export default App
