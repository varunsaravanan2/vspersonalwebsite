/*
  Entry point: the first code that runs in the browser.
  It finds <div id="root"> in index.html and renders the React app into it.
*/

import { MotionConfig } from 'motion/react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')!).render(
  // StrictMode (development only) runs effects twice on purpose to expose
  // bugs like missing cleanup functions. It has no effect in production.
  <StrictMode>
    {/*
      BrowserRouter keeps the URL in sync with the screen being shown, using
      real paths like /projects (not /#/projects), so links can be shared
      and the back button works.
    */}
    <BrowserRouter>
      {/*
        reducedMotion="user": if the visitor's OS has "reduce motion" turned on,
        Motion skips movement animations automatically. Accessibility for free.
      */}
      <MotionConfig reducedMotion="user">
        <App />
      </MotionConfig>
    </BrowserRouter>
  </StrictMode>,
)
