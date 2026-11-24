import { FREQUENCIES, MODULES, groupItemsByModule, newItem } from '../utils.js'

export default function PlaybookEditor({ items, onChange }) {
  const updateItem = (id, patch) =>
    onChange(items.map((item) => (item.id === id ? { ...item, ...patch } : item)))

  const updateDetails = (id, patch) =>
    onChange(items.map((item) => (item.id === id ? { ...item, details: { ...item.details, ...patch } } : item)))

  const removeItem = (id) => onChange(items.filter((item) => item.id !== id))

  const addItem = (module) => onChange([...items, newItem(module)])

  const groups = groupItemsByModule(items)

  return (
    <div className="stack">
      {MODULES.map((module) => {
        const group = groups.find((entry) => entry.key === module.key)
        const moduleItems = group ? group.items : []
        return (
          <section key={module.key} className="stack">
            <div className="section-head">
              <h3 className="group-title">{module.label}</h3>
              <button type="button" className="btn btn-ghost" onClick={() => addItem(module.key)}>
                Add item
              </button>
            </div>
            {moduleItems.length === 0 && <p className="muted small">No items in this section.</p>}
            {moduleItems.map((item) => (
              <div key={item.id} className="card stack-tight">
                <div className="row-between wrap">
                  <input
                    aria-label={`${module.label} title`}
                    value={item.title}
                    placeholder="Title"
                    maxLength={200}
                    onChange={(event) => updateItem(item.id, { title: event.target.value })}
                  />
                  <button type="button" className="btn btn-danger-ghost" onClick={() => removeItem(item.id)}>
                    Remove
                  </button>
                </div>
                <ModuleFields item={item} onDetails={(patch) => updateDetails(item.id, patch)} />
              </div>
            ))}
          </section>
        )
      })}
    </div>
  )
}

function ModuleFields({ item, onDetails }) {
  const details = item.details || {}

  if (item.module === 'responsibility') {
    return (
      <div className="grid-2">
        <label className="field">
          Frequency
          <select value={details.frequency} onChange={(event) => onDetails({ frequency: event.target.value })}>
            {FREQUENCIES.map((frequency) => (
              <option key={frequency} value={frequency}>{frequency}</option>
            ))}
          </select>
        </label>
        <label className="field">
          Estimated minutes
          <input
            type="number"
            min="0"
            max="1440"
            value={details.estimated_minutes ?? 0}
            onChange={(event) => onDetails({ estimated_minutes: Number(event.target.value) || 0 })}
          />
        </label>
        <label className="field span-2">
          Steps (one per line)
          <textarea
            rows={4}
            value={(details.steps || []).join('\n')}
            onChange={(event) => onDetails({ steps: event.target.value.split('\n') })}
          />
        </label>
      </div>
    )
  }

  if (item.module === 'access') {
    return (
      <div className="grid-2">
        <label className="field">
          Tool or dashboard URL
          <input
            type="url"
            value={details.url || ''}
            maxLength={500}
            onChange={(event) => onDetails({ url: event.target.value })}
          />
        </label>
        <label className="field">
          Access permission needed
          <input
            value={details.permission || ''}
            maxLength={300}
            onChange={(event) => onDetails({ permission: event.target.value })}
          />
        </label>
      </div>
    )
  }

  if (item.module === 'stakeholder') {
    return (
      <div className="grid-2">
        <label className="field">
          Role
          <input
            value={details.role || ''}
            maxLength={160}
            onChange={(event) => onDetails({ role: event.target.value })}
          />
        </label>
        <label className="field">
          Contact when
          <input
            value={details.contact_when || ''}
            maxLength={300}
            onChange={(event) => onDetails({ contact_when: event.target.value })}
          />
        </label>
      </div>
    )
  }

  return (
    <label className="field">
      How to avoid it
      <textarea
        rows={2}
        maxLength={800}
        value={details.guidance || ''}
        onChange={(event) => onDetails({ guidance: event.target.value })}
      />
    </label>
  )
}
