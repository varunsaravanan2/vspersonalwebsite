/*
  Title screen: the landing page at "/".

  Like the game's title screen: name, role, and a blinking "Press start".
  Any key, click, or tap goes to the main menu.
*/

import { motion } from 'motion/react'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './TitleScreen.module.css'

export default function TitleScreen() {
  const navigate = useNavigate()

  // "Press any key": listen on the whole window, not just one element.
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      // Ignore Tab and modifier keys, so keyboard users can still Tab to
      // the button (and use shortcuts like Cmd+R) without being whisked away.
      if (['Tab', 'Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) return
      navigate('/menu')
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [navigate])

  return (
    <motion.main
      className={styles.title}
      onClick={() => navigate('/menu')}
      // Leaving the title screen zooms in and fades, like pressing start in the game.
      exit={{ opacity: 0, scale: 1.08 }}
      transition={{ duration: 0.3 }}
    >
      {/*
        The emblem: my initials, VS, which also happen to be Smash's
        "versus" symbol. Original artwork instead of Nintendo's logo.
        aria-hidden because it's decorative; the name below is the real heading.
      */}
      <div className={styles.emblem} aria-hidden="true">
        VS
      </div>

      <h1 className={styles.name}>
        Varun Saravanan
        <span className={styles.role}>Software Engineer</span>
      </h1>

      {/*
        A real <button>, so keyboard and screen-reader users have an obvious
        way in, not just "press anything". stopPropagation stops the click
        from also reaching <main>'s onClick and navigating twice.
      */}
      <button
        type="button"
        className={styles.press}
        onClick={(e) => {
          e.stopPropagation()
          navigate('/menu')
        }}
      >
        Press start
      </button>
    </motion.main>
  )
}
