/*
  App: maps each URL to a screen, and animates between screens.

  Every Smash menu is a real page with its own URL:
    /                -> title screen
    /menu            -> main menu
    /projects        -> character select (projects)
    /projects/:slug  -> fighter page (one project)
    /skills          -> spirit board
    /experience      -> stage select
    /about           -> vault
    /contact         -> challenger approaching
*/

import { AnimatePresence } from 'motion/react'
import { Route, Routes, useLocation } from 'react-router-dom'
import ComingSoon from './screens/ComingSoon'
import MainMenu from './screens/MainMenu'
import NotFound from './screens/NotFound'
import TitleScreen from './screens/TitleScreen'

export default function App() {
  const location = useLocation()

  return (
    /*
      AnimatePresence is what makes exit animations possible. Normally React
      removes the old screen instantly when the URL changes. AnimatePresence
      keeps it on screen until its `exit` animation finishes (see Screen.tsx).

      mode="wait": finish the old screen's exit before the new one enters,
      so two screens never overlap.
    */
    <AnimatePresence mode="wait">
      {/*
        Passing `location` and `key` explicitly: the key changes on every
        navigation, which tells AnimatePresence "this is a different screen".
        Routes uses the same `location`, so the leaving screen keeps rendering
        its own content during its exit animation instead of the new page's.
      */}
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<TitleScreen />} />
        <Route path="/menu" element={<MainMenu />} />

        {/* Placeholders until each screen is built in the next steps. */}
        <Route path="/projects" element={<ComingSoon title="Character select" color="var(--p1)" />} />
        <Route path="/projects/:slug" element={<ComingSoon title="Fighter page" color="var(--p1)" />} />
        <Route path="/skills" element={<ComingSoon title="Spirit board" color="var(--p2)" />} />
        <Route path="/experience" element={<ComingSoon title="Stage select" color="var(--p3)" />} />
        <Route path="/about" element={<ComingSoon title="Vault" color="var(--p4)" />} />
        <Route path="/contact" element={<ComingSoon title="Challenger approaching" color="var(--p1)" />} />

        {/* "*" matches any URL not listed above. */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AnimatePresence>
  )
}
