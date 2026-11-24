import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="navbar">
      <Link to="/" className="brand">KeyPass</Link>
      <nav className="nav-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/kits/new">New kit</NavLink>
      </nav>
      <div className="nav-user">
        <span className="muted">{user.full_name}</span>
        <button type="button" className="btn btn-ghost" onClick={handleLogout}>Log out</button>
      </div>
    </header>
  )
}
