import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { extractErrorMessage, kitApi } from '../api.js'
import { Alert, ProgressBar, Spinner, StatusBadge } from '../components/common.jsx'
import PlaybookEditor from '../components/PlaybookEditor.jsx'
import ReadinessBrief from '../components/ReadinessBrief.jsx'
import ReadinessChecklist from '../components/ReadinessChecklist.jsx'
import { formatDate, formatDateTime, handoverTiming } from '../utils.js'

export default function KitDetail() {
  const { kitId } = useParams()
  const [kit, setKit] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState('')
  const [draft, setDraft] = useState(null)

  const load = useCallback(() => {
    kitApi.get(kitId).then(setKit).catch((err) => setError(extractErrorMessage(err)))
  }, [kitId])

  useEffect(() => {
    load()
  }, [load])

  const runAction = async (key, action, successMessage) => {
    setBusy(key)
    setError('')
    setNotice('')
    try {
      const updated = await action()
      setKit(updated)
      if (successMessage) setNotice(successMessage)
      return true
    } catch (err) {
      setError(extractErrorMessage(err))
      return false
    } finally {
      setBusy('')
    }
  }

  if (!kit) {
    return error ? (
      <div className="stack">
        <Link to="/" className="back-link">Back to dashboard</Link>
        <Alert>{error}</Alert>
      </div>
    ) : (
      <Spinner label="Loading transition kit..." />
    )
  }

  const isOwner = kit.role === 'owner'
  const counterpart = isOwner ? kit.successor : kit.owner
  const permissions = kit.permissions

  const handleProgress = (itemId, progress) =>
    runAction(`progress-${itemId}`, () => kitApi.updateProgress(kit.id, itemId, progress))

  const handlePost = (itemId, text) =>
    runAction(`thread-${itemId}`, () => kitApi.postMessage(kit.id, itemId, text))

  const handleReadiness = () =>
    runAction('readiness', () => kitApi.readinessCheck(kit.id), 'Readiness check complete.')

  const handleSignOff = () => {
    const confirmed = window.confirm(
      'Confirm final handover sign-off? The kit will be locked and playbook edits and progress changes will stop.'
    )
    if (!confirmed) return
    runAction('signoff', () => kitApi.signOff(kit.id), 'Handover signed off. The kit is now locked.')
  }

  const startEditing = () => setDraft({ title: kit.title, handover_date: kit.handover_date, items: kit.items })

  const saveDraft = async () => {
    const saved = await runAction('save', () => kitApi.updatePlaybook(kit.id, draft), 'Playbook saved.')
    if (saved) setDraft(null)
  }

  return (
    <div className="stack">
      <Link to="/" className="back-link">Back to dashboard</Link>
      <Alert>{error}</Alert>
      <Alert type="success">{notice}</Alert>

      <section className="card stack">
        <div className="row-between wrap">
          <div className="stack-tight">
            <h1>{kit.title}</h1>
            <p className="muted">
              {isOwner ? 'Handing over to' : 'Taking over from'} <strong>{counterpart.full_name}</strong>{' '}
              ({counterpart.designation})
            </p>
            <p className="muted">
              Handover {formatDate(kit.handover_date)} | {handoverTiming(kit.handover_date, kit.status)}
            </p>
          </div>
          <StatusBadge status={kit.status} />
        </div>
        <ProgressBar value={kit.readiness_percent} label="Successor readiness" />
        {kit.status === 'Completed' && (
          <p className="muted">
            Signed off by {kit.completed_by?.full_name} on {formatDateTime(kit.completed_at)}.
          </p>
        )}
        <div className="action-row">
          {permissions.run_readiness_check && (
            <button type="button" className="btn btn-primary" disabled={!!busy} onClick={handleReadiness}>
              {busy === 'readiness' ? 'Running readiness check...' : 'Run Readiness Check'}
            </button>
          )}
          {permissions.sign_off && (
            <button type="button" className="btn btn-success" disabled={!!busy} onClick={handleSignOff}>
              {busy === 'signoff' ? 'Signing off...' : 'Confirm Final Handover Sign-Off'}
            </button>
          )}
          {permissions.edit_playbook && !draft && (
            <button type="button" className="btn btn-ghost" onClick={startEditing}>Edit playbook</button>
          )}
        </div>
      </section>

      <ReadinessBrief brief={kit.last_readiness_brief} />

      {isOwner && kit.raw_notes && (
        <details className="card">
          <summary>Original knowledge dump</summary>
          <pre className="raw-notes">{kit.raw_notes}</pre>
        </details>
      )}

      {draft ? (
        <section className="card stack">
          <h2>Edit playbook</h2>
          <div className="grid-2">
            <label className="field">
              Title
              <input
                value={draft.title}
                maxLength={160}
                onChange={(event) => setDraft({ ...draft, title: event.target.value })}
              />
            </label>
            <label className="field">
              Handover date
              <input
                type="date"
                value={draft.handover_date}
                onChange={(event) => setDraft({ ...draft, handover_date: event.target.value })}
              />
            </label>
          </div>
          <PlaybookEditor items={draft.items} onChange={(items) => setDraft({ ...draft, items })} />
          <div className="action-row">
            <button type="button" className="btn btn-primary" disabled={!!busy} onClick={saveDraft}>
              {busy === 'save' ? 'Saving...' : 'Save playbook'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => setDraft(null)}>Cancel</button>
          </div>
        </section>
      ) : (
        <section className="stack">
          <h2>Readiness checklist</h2>
          <ReadinessChecklist
            items={kit.items}
            canUpdateProgress={permissions.update_progress}
            onProgress={handleProgress}
            onPost={handlePost}
          />
        </section>
      )}
    </div>
  )
}
