import { formatDateTime } from '../utils.js'

export default function ReadinessBrief({ brief }) {
  if (!brief) return null

  return (
    <section className="card stack">
      <div className="row-between wrap">
        <h2>Transition Readiness Summary</h2>
        <span className="small muted">
          Generated {formatDateTime(brief.generated_at)} by {brief.generated_by}
        </span>
      </div>
      <BriefBlock title="Ready to Transfer" items={brief.ready_to_transfer} />
      <BriefBlock title="Critical Gaps Before Handover Date" items={brief.critical_gaps} />
      <BriefBlock title="Recommended Final Sync Agenda" items={brief.sync_agenda} ordered />
    </section>
  )
}

function BriefBlock({ title, items, ordered = false }) {
  const ListTag = ordered ? 'ol' : 'ul'
  return (
    <div className="brief-block">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="muted">Nothing flagged.</p>
      ) : (
        <ListTag>
          {items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ListTag>
      )}
    </div>
  )
}
