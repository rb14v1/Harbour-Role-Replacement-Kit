import { useState } from 'react'
import { formatDateTime } from '../utils.js'

export default function ItemThread({ thread = [], onPost }) {
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    const value = text.trim()
    if (!value) return
    setSending(true)
    const posted = await onPost(value)
    if (posted) setText('')
    setSending(false)
  }

  return (
    <div className="thread">
      {thread.length > 0 && (
        <ul className="thread-list">
          {thread.map((message) => (
            <li key={message.id} className="thread-msg">
              <div className="small muted">
                <strong>{message.author_name}</strong>{' '}
                <span className={`role-tag role-${message.author_role}`}>
                  {message.author_role === 'owner' ? 'Outgoing owner' : 'Successor'}
                </span>{' '}
                | {formatDateTime(message.created_at)}
              </div>
              <p>{message.text}</p>
            </li>
          ))}
        </ul>
      )}
      <form className="thread-form" onSubmit={submit}>
        <textarea
          aria-label="Clarification question or reply"
          rows={2}
          maxLength={1000}
          placeholder="Ask a clarification question or reply..."
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <button type="submit" className="btn btn-ghost" disabled={sending || !text.trim()}>
          {sending ? 'Posting...' : 'Post'}
        </button>
      </form>
    </div>
  )
}
