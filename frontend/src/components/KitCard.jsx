import { Link } from 'react-router-dom'
import { ProgressBar, StatusBadge } from './common.jsx'
import { formatDate, handoverTiming } from '../utils.js'

export default function KitCard({ kit }) {
  const counterpart = kit.role === 'owner' ? `Successor: ${kit.successor.full_name}` : `From: ${kit.owner.full_name}`

  return (
    <Link to={`/kits/${kit.id}`} className="card kit-card">
      <div className="row-between wrap">
        <h3>{kit.title}</h3>
        <StatusBadge status={kit.status} />
      </div>
      <p className="muted">{counterpart}</p>
      <p className="muted small">
        Handover {formatDate(kit.handover_date)} | {handoverTiming(kit.handover_date, kit.status)}
      </p>
      <ProgressBar value={kit.readiness_percent} label="Successor readiness" />
      {kit.open_questions > 0 && (
        <p className="small warn">{kit.open_questions} open question{kit.open_questions === 1 ? '' : 's'}</p>
      )}
    </Link>
  )
}
