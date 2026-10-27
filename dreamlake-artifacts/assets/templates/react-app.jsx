// kind: react — `React` is a global (no imports); define a top-level `App`.
// Tailwind utility classes compile at runtime. Return one root element.
function App() {
  const [n, setN] = React.useState(0)
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold tracking-tight">Counter</h1>
      <button
        className="px-4 py-2 rounded-lg border border-current/20 hover:bg-current/5"
        onClick={() => setN((v) => v + 1)}
      >
        clicked {n} times
      </button>
    </div>
  )
}
