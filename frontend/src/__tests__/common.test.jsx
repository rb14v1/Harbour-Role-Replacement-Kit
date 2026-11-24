import { render, screen } from '@testing-library/react'
import { Alert, EmptyState, ProgressBar, StatusBadge } from '../components/common.jsx'

describe('ProgressBar', () => {
  it('shows the percentage and exposes it to assistive technology', () => {
    render(<ProgressBar value={42} label="Successor readiness" />)
    expect(screen.getByText('42%')).toBeInTheDocument()
    expect(screen.getByRole('progressbar', { name: 'Successor readiness' })).toHaveAttribute('aria-valuenow', '42')
  })

  it('clamps out-of-range values', () => {
    render(<ProgressBar value={180} />)
    expect(screen.getByText('100%')).toBeInTheDocument()
  })
})

describe('Alert', () => {
  it('renders nothing when there is no message', () => {
    const { container } = render(<Alert />)
    expect(container).toBeEmptyDOMElement()
  })

  it('announces error messages as alerts', () => {
    render(<Alert>Something failed.</Alert>)
    expect(screen.getByRole('alert')).toHaveTextContent('Something failed.')
  })
})

describe('StatusBadge and EmptyState', () => {
  it('labels completed kits distinctly', () => {
    render(<StatusBadge status="Completed" />)
    expect(screen.getByText('Completed')).toHaveClass('badge-done')
  })

  it('renders empty state copy', () => {
    render(<EmptyState>No kits yet.</EmptyState>)
    expect(screen.getByText('No kits yet.')).toBeInTheDocument()
  })
})
