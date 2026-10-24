/*
  Main menu: the hub that links to every section.

  Each tile shows the Smash name big and the plain meaning underneath,
  so a recruiter who has never played the game still knows where to click.
*/

import { motion, type Variants } from 'motion/react'
import { useRef, type CSSProperties, type KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import Screen from '../components/Screen'
import styles from './MainMenu.module.css'

// The menu as data instead of five hand-written <Link>s: adding a section
// means adding one line here, and the order in this array is the
// arrow-key order too.
const TILES = [
  { to: '/projects', game: 'Smash', label: 'Projects', color: 'var(--p1)', big: true },
  { to: '/skills', game: 'Spirits', label: 'Skills', color: 'var(--p2)' },
  { to: '/experience', game: 'Stages', label: 'Experience', color: 'var(--p3)' },
  { to: '/about', game: 'Vault', label: 'About me', color: 'var(--p4)' },
  { to: '/contact', game: 'Online', label: 'Contact', color: 'var(--fg)' },
]

/*
  Motion "variants": named animation states that a parent passes down to its
  children. The parent's staggerChildren starts each tile 60ms after the
  previous one, so they slide in one by one like the game's menu.
*/
const list: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06, delayChildren: 0.15 } },
}
const tile: Variants = {
  hidden: { opacity: 0, x: 60 },
  show: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 380, damping: 30 } },
}

export default function MainMenu() {
  // Refs give direct access to each tile's DOM element, needed to move
  // keyboard focus with the arrow keys. useRef keeps the same array across
  // renders without causing a re-render when it changes.
  const tileRefs = useRef<(HTMLAnchorElement | null)[]>([])

  // Arrow keys move between tiles like a controller's d-pad.
  // Tab still works too; this is an extra, not a replacement.
  function onKeyDown(e: KeyboardEvent<HTMLElement>) {
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]
    if (!step) return
    e.preventDefault() // stop the arrow key from also scrolling the page

    const current = tileRefs.current.findIndex((el) => el === document.activeElement)
    // Wrap around: right from the last tile goes back to the first.
    // (+ TILES.length keeps the result positive when stepping left from 0.)
    const next = current === -1 ? 0 : (current + step + TILES.length) % TILES.length
    tileRefs.current[next]?.focus()
  }

  return (
    <Screen title="Main menu" color="var(--p1)" backTo="/">
      {/* <nav> tells screen readers this is the site's main navigation. */}
      <motion.nav
        className={styles.grid}
        aria-label="Main menu"
        onKeyDown={onKeyDown}
        variants={list}
        initial="hidden"
        animate="show"
      >
        {TILES.map((t, i) => (
          <motion.div key={t.to} variants={tile} className={t.big ? styles.big : undefined}>
            <Link
              to={t.to}
              ref={(el) => {
                tileRefs.current[i] = el
              }}
              className={styles.tile}
              style={{ '--tile': t.color } as CSSProperties}
            >
              <span className={styles.game}>{t.game}</span>
              <span className={styles.label}>{t.label}</span>
            </Link>
          </motion.div>
        ))}
      </motion.nav>

      <p className={styles.hint}>
        <kbd>←</kbd> <kbd>→</kbd> to move · <kbd>Enter</kbd> to select · <kbd>Esc</kbd> to go back
      </p>
    </Screen>
  )
}
