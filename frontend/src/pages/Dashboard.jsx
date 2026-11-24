import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { extractErrorMessage, kitApi } from '../api.js'
import { Alert, EmptyState, Spinner } from '../components/common.jsx'
import KitCard from '../components/KitCard.jsx'

export default function Dashboard() {
  const [handingOver, setHandingOver] = useState(null)
  const [takingOver, setTakingOver] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([kitApi.list('owner'), kitApi.list('successor')])
      .then(([owned, successing]) => {
        setHandingOver(owned)
        setTakingOver(successing)
      })
      .catch((err) => {
        setError(extractErrorMessage(err))
        setHandingOver([])
        setTakingOver([])
      })
  }, [])

  return (
    <div className="stack">
      <h1>Role Transition Dashboard</h1>
      <Alert>{error}</Alert>
      <div className="dashboard-grid">
        <section className="card stack">
          <h2>Kits I&apos;m Handing Over</h2>
          <KitList kits={handingOver} emptyText="You have not created any transition kits yet." />
        </section>
        <section className="card stack">
          <h2>Kits I&apos;m Taking Over</h2>
          <KitList kits={takingOver} emptyText="No kits have been assigned to you as successor." />
        </section>
        <section className="card stack">
          <h2>Create New Transition Kit</h2>
          <p className="muted">
            Describe the role, pick a successor and let AI turn your notes into a structured playbook you can review
            before publishing.
          </p>
          <Link to="/kits/new" className="btn btn-primary">Start a new kit</Link>
        </section>
      </div>
    </div>
  )
}

function KitList({ kits, emptyText }) {
  if (kits === null) return <Spinner label="Loading kits..." />
  if (kits.length === 0) return <EmptyState>{emptyText}</EmptyState>
  return (
    <div className="stack">
      {kits.map((kit) => (
        <KitCard key={kit.id} kit={kit} />
      ))}
    </div>
  )
}
