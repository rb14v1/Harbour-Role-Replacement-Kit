import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi, extractErrorMessage, kitApi } from '../api.js'
import { Alert, Spinner } from '../components/common.jsx'
import PlaybookEditor from '../components/PlaybookEditor.jsx'
import { groupByDepartment, todayIso } from '../utils.js'

const MIN_NOTES_LENGTH = 20

export default function CreateKit() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', handover_date: '', successor_id: '', raw_notes: '' })
  const [directory, setDirectory] = useState(null)
  const [items, setItems] = useState([])
  const [generated, setGenerated] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  useEffect(() => {
    authApi
      .directory()
      .then(setDirectory)
      .catch((err) => {
        setError(extractErrorMessage(err))
        setDirectory([])
      })
  }, [])

  const departments = useMemo(() => groupByDepartment(directory || []), [directory])

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }))
  }

  const buildPlaybook = async () => {
    setError('')
    if (!form.title.trim()) {
      setError('Enter a role or responsibility title before building the playbook.')
      return
    }
    if (form.raw_notes.trim().length < MIN_NOTES_LENGTH) {
      setError(`Add at least ${MIN_NOTES_LENGTH} characters of knowledge notes so the AI has enough to work with.`)
      return
    }
    setStatus('building')
    try {
      const result = await kitApi.generatePlaybook({
        role_title: form.title.trim(),
        raw_notes: form.raw_notes.trim(),
      })
      setItems(result.items)
      setGenerated(true)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setStatus('')
    }
  }

  const publish = async () => {
    setError('')
    if (!form.successor_id || !form.handover_date) {
      setError('Choose a successor and a target handover date before publishing.')
      return
    }
    if (items.length === 0) {
      setError('Add at least one playbook item before publishing.')
      return
    }
    setStatus('publishing')
    try {
      const kit = await kitApi.create({
        title: form.title.trim(),
        handover_date: form.handover_date,
        successor_id: form.successor_id,
        raw_notes: form.raw_notes.trim(),
        items,
      })
      navigate(`/kits/${kit.id}`)
    } catch (err) {
      setError(extractErrorMessage(err))
      setStatus('')
    }
  }

  return (
    <div className="stack">
      <h1>Create a Role Transition Kit</h1>
      <Alert>{error}</Alert>

      <section className="card stack">
        <h2>1. Describe the handover</h2>
        <div className="grid-2">
          <label className="field">
            Role or responsibility title
            <input
              name="title"
              maxLength={160}
              placeholder="e.g. Weekly Client Reporting & Sprint Operations"
              value={form.title}
              onChange={handleChange}
            />
          </label>
          <label className="field">
            Target handover date
            <input
              name="handover_date"
              type="date"
              min={todayIso()}
              value={form.handover_date}
              onChange={handleChange}
            />
          </label>
          <label className="field span-2">
            Successor
            {directory === null ? (
              <Spinner label="Loading colleagues..." />
            ) : (
              <select name="successor_id" value={form.successor_id} onChange={handleChange}>
                <option value="">Select a teammate</option>
                {departments.map((group) => (
                  <optgroup key={group.department} label={group.department}>
                    {group.members.map((person) => (
                      <option key={person.id} value={person.id}>
                        {person.full_name} ({person.designation})
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            )}
          </label>
        </div>
        <label className="field">
          Raw knowledge dump
          <textarea
            name="raw_notes"
            rows={10}
            maxLength={20000}
            placeholder="Paste messy notes: recurring tasks, tool links, stakeholder contacts, gotchas and unwritten rules."
            value={form.raw_notes}
            onChange={handleChange}
          />
        </label>
        <div className="action-row">
          <button type="button" className="btn btn-primary" disabled={!!status} onClick={buildPlaybook}>
            {status === 'building' ? 'Organising your notes...' : 'Build Structured Playbook'}
          </button>
        </div>
      </section>

      <section className="card stack">
        <h2>2. Review the playbook</h2>
        <p className="muted">
          {generated
            ? 'Review the AI draft. Edit, add or remove anything before publishing to your successor.'
            : 'Build the playbook with AI, or add items manually.'}
        </p>
        <PlaybookEditor items={items} onChange={setItems} />
        <div className="action-row">
          <button type="button" className="btn btn-success" disabled={!!status} onClick={publish}>
            {status === 'publishing' ? 'Publishing...' : 'Publish Transition Kit'}
          </button>
        </div>
      </section>
    </div>
  )
}
