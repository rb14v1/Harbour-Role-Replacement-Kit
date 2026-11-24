import { Navigate, Route, Routes } from 'react-router-dom'
import { Spinner } from './components/common.jsx'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { useAuth } from './context/AuthContext.jsx'
import CreateKit from './pages/CreateKit.jsx'
import Dashboard from './pages/Dashboard.jsx'
import KitDetail from './pages/KitDetail.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="page-center">
        <Spinner label="Loading KeyPass..." />
      </div>
    )
  }

  return (
    <>
      {user && <Navbar />}
      <main className="container">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
          <Route path="/register" element={user ? <Navigate to="/" replace /> : <Register />} />
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/kits/new" element={<ProtectedRoute><CreateKit /></ProtectedRoute>} />
          <Route path="/kits/:kitId" element={<ProtectedRoute><KitDetail /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
