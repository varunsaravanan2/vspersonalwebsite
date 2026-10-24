/*
  Screen: the shared wrapper around every page except the title screen.

  It gives each page the same three things, so no screen repeats them:
  1. The diagonal "slash" wipe when entering and leaving
  2. A header with a back button and the screen's name
  3. Escape-key "back", like pressing B on a controller
*/

import { motion } from 'motion/react'
import { useEffect, type CSSProperties, type ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import styles from './Screen.module.css'

interface ScreenProps {
  title: string
  /** Accent color for this section, e.g. "var(--p1)". */
  color: string
  /** Where "back" goes. Defaults to the main menu. */
  backTo?: string
  children: ReactNode
}

export default function Screen({ title, color, backTo = '/menu', children }: ScreenProps) {
  const navigate = useNavigate()

  // Escape = "back". The listener is added when the screen appears and
  // removed in the cleanup function when it leaves. Without the cleanup,
  // every visit would stack another listener and Escape would fire many times.
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') navigate(backTo)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [navigate, backTo])

  return (
    <motion.main
      className={styles.screen}
      // A CSS variable set per screen; the CSS file uses var(--accent),
      // so one stylesheet works for every section color.
      style={{ '--accent': color } as CSSProperties}
      /*
        The slash wipe. clip-path cuts the element to a polygon; animating
        the polygon's points reveals the screen along a diagonal edge.
        initial = before entering, animate = fully shown, exit = leaving.
      */
      initial={{ clipPath: 'polygon(0 0, 0 0, -20% 100%, 0 100%)' }}
      animate={{ clipPath: 'polygon(0 0, 120% 0, 100% 100%, 0 100%)' }}
      exit={{ opacity: 0, x: -40 }}
      // Under 400ms: long enough to feel like Smash, short enough that
      // a recruiter clicking around never waits on it.
      transition={{ duration: 0.35, ease: 'easeOut' }}
    >
      <header className={styles.header}>
        <Link to={backTo} className={styles.back} aria-label="Back">
          {/* aria-hidden: screen readers read "Back" from aria-label instead of the arrow. */}
          <span aria-hidden="true">◀</span> Back
          <kbd className={styles.kbd}>Esc</kbd>
        </Link>
        <h1 className={styles.title}>{title}</h1>
      </header>
      {children}
    </motion.main>
  )
}
