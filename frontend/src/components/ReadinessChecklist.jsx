import { EmptyState } from './common.jsx'
import ItemThread from './ItemThread.jsx'
import { PROGRESS_STATES, groupItemsByModule, isSafeUrl, progressClass } from '../utils.js'

export default function ReadinessChecklist({ items, canUpdateProgress, onProgress, onPost }) {
  const groups = groupItemsByModule(items)

  if (groups.length === 0) {
    return <EmptyState>No playbook items yet.</EmptyState>
  }

  return (
    <div className="stack">
      {groups.map((group) => (
        <section key={group.key} className="stack">
          <h3 className="group-title">{group.label}</h3>
          {group.items.map((item) => (
            <article key={item.id} className="card checklist-item">
              <div className="row-between wrap">
                <div className="stack-tight">
                  <h4>{item.title}</h4>
                  <ItemDetails item={item} />
                </div>
                {canUpdateProgress ? (
                  <select
                    aria-label={`Progress for ${item.title}`}
                    value={item.progress}
                    onChange={(event) => onProgress(item.id, event.target.value)}
                  >
                    {PROGRESS_STATES.map((state) => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                ) : (
                  <span className={`badge ${progressClass(item.progress)}`}>{item.progress}</span>
                )}
              </div>
              <ItemThread thread={item.thread} onPost={(text) => onPost(item.id, text)} />
            </article>
          ))}
        </section>
      ))}
    </div>
  )
}

function ItemDetails({ item }) {
  const details = item.details || {}

  if (item.module === 'responsibility') {
    const steps = details.steps || []
    return (
      <div className="small muted">
        <span>{details.frequency}</span> | <span>{details.estimated_minutes ? `${details.estimated_minutes} min` : 'time not estimated'}</span>
        {steps.length > 0 && (
          <ol>
            {steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        )}
      </div>
    )
  }

  if (item.module === 'access') {
    return (
      <div className="small muted">
        {details.url && isSafeUrl(details.url) && (
          <a href={details.url} target="_blank" rel="noreferrer">{details.url}</a>
        )}
        <p>Access needed: {details.permission || 'not specified'}</p>
      </div>
    )
  }

  if (item.module === 'stakeholder') {
    return <p className="small muted">{details.role}. Contact when: {details.contact_when}</p>
  }

  return <p className="small muted">{details.guidance}</p>
}
