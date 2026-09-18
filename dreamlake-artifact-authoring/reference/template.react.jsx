// DreamLake `react` starter — defines a top-level `App`, no imports.
//
// Tailwind utilities DO compile for this kind, so layout is Tailwind and
// the look comes from the house tokens. Inject house-style.css through a
// <style> tag (there is no stylesheet to link and the CSP blocks URLs);
// the token custom properties then cascade to everything below, and
// Tailwind arbitrary values like bg-[var(--dl-panel)] pick them up.

const HOUSE_STYLE = `
/* ── PASTE house-style.css HERE, verbatim. ── */
/* ── then the <style> block of theme-toggle.html ── */
`

// Light / system / dark, same contract as the app: 'system' drops the
// attribute so the media query decides. See reference/theme-toggle.html.
const THEMES = ['light', 'system', 'dark']

function ThemePill() {
  const [theme, setTheme] = React.useState(() => {
    try {
      const v = localStorage.getItem('dl-theme')
      return THEMES.includes(v) ? v : 'system'
    } catch (e) { return 'system' }
  })
  React.useEffect(() => {
    if (theme === 'system') document.documentElement.removeAttribute('data-theme')
    else document.documentElement.setAttribute('data-theme', theme)
    try { localStorage.setItem('dl-theme', theme) } catch (e) {}
  }, [theme])

  return (
    <div className="theme-pill" role="group" aria-label="Theme">
      <span className="indicator" aria-hidden
            style={{ transform: `translateX(${THEMES.indexOf(theme) * 22}px)` }} />
      {THEMES.map((t) => (
        <button key={t} type="button" aria-label={t + ' mode'} title={t + ' mode'}
                aria-pressed={theme === t} onClick={() => setTheme(t)}>
          {/* inline the matching Lucide icon from theme-toggle.html */}
        </button>
      ))}
    </div>
  )
}

function Card({ label, value }) {
  return (
    <div className="dl-card flex flex-col gap-1">
      <span className="dl-caption">{label}</span>
      <span className="text-2xl tabular-nums">{value}</span>
    </div>
  )
}

function App() {
  const [selected, setSelected] = React.useState(null)

  // Real data, embedded — the frame has no network.
  const rows = [
    { id: 'a', label: 'Episodes', value: '1,284' },
    { id: 'b', label: 'Success rate', value: '98.2%' },
  ]

  return (
    <>
      <style>{HOUSE_STYLE}</style>
      <main className="mx-auto flex max-w-3xl flex-col gap-8 p-6">
        <header className="flex flex-col gap-2 border-b pb-6"
                style={{ borderColor: 'var(--dl-stroke)' }}>
          <div className="flex items-center justify-between gap-4">
            <span className="dl-chip dl-chip--accent w-fit">Real label</span>
            <ThemePill />
          </div>
          <h1>The actual subject of this artifact</h1>
          <p className="dl-caption">One line saying what a reader gets from it.</p>
        </header>

        <section className="grid gap-4 sm:grid-cols-2">
          {rows.map((r) => <Card key={r.id} label={r.label} value={r.value} />)}
        </section>

        <div className="flex gap-2">
          {rows.map((r) => (
            <button
              key={r.id}
              className={`dl-btn ${selected === r.id ? 'dl-btn--primary' : ''}`}
              onClick={() => setSelected(r.id)}
            >
              {r.label}
            </button>
          ))}
        </div>
      </main>
    </>
  )
}
