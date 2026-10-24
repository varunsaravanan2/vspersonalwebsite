/*
  Temporary placeholder for screens that aren't built yet.
  Each route in App.tsx gets swapped for its real screen in the next steps,
  and this file gets deleted once none are left.
*/

import Screen from '../components/Screen'

export default function ComingSoon({ title, color }: { title: string; color: string }) {
  return (
    <Screen title={title} color={color}>
      <p style={{ color: 'var(--muted)', margin: 0 }}>This screen is still being built.</p>
    </Screen>
  )
}
