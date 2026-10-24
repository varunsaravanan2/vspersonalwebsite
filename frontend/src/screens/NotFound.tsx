/*
  404 page for any URL that doesn't match a route.
  Styled like falling off the stage in Smash: you got knocked off,
  here's the way back.
*/

import { Link } from 'react-router-dom'
import Screen from '../components/Screen'

export default function NotFound() {
  return (
    <Screen title="KO!" color="var(--p1)">
      <p style={{ color: 'var(--muted)', margin: 0, maxWidth: '60ch' }}>
        This page got launched off the stage. It doesn't exist, or it moved.{' '}
        <Link to="/menu">Back to the main menu</Link>
      </p>
    </Screen>
  )
}
