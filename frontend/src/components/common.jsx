export function Alert({ type = 'error', children }) {
  if (!children) return null
  return (
    <div className={`alert alert-${type}`} role={type === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  )
}

export function Spinner({ label = 'Loading...' }) {
  return (
    <div className="spinner-wrap" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export function ProgressBar({ value, label = 'Readiness' }) {
  const percent = Math.max(0, Math.min(100, Number(value) || 0))
  return (
    <div className="progress">
      <div
        className="progress-track"
        role="progressbar"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
      >
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <span className="progress-value">{percent}%</span>
    </div>
  )
}

export function StatusBadge({ status }) {
  return <span className={`badge ${status === 'Completed' ? 'badge-done' : 'badge-active'}`}>{status}</span>
}

export function EmptyState({ children }) {
  return <p className="empty-state">{children}</p>
}
