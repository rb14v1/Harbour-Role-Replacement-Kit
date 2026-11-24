import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { extractErrorMessage } from '../api.js'
import { DEPARTMENTS, validateRegistration } from '../accountRules.js'
import { Alert } from '../components/common.jsx'
import { useAuth } from '../context/AuthContext.jsx'

const EMPTY_FORM = { full_name: '', email: '', department: '', designation: '', password: '' }

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY_FORM)
  const [fieldErrors, setFieldErrors] = useState({})
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const designations = DEPARTMENTS[form.department] || []

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({
      ...prev,
      [name]: value,
      ...(name === 'department' ? { designation: '' } : {}),
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    const errors = validateRegistration(form)
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return

    setSubmitting(true)
    try {
      await register({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        department: form.department.trim(),
        designation: form.designation.trim(),
        password: form.password,
      })
      navigate('/', { replace: true })
    } catch (err) {
      setError(extractErrorMessage(err))
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="card auth-card stack" onSubmit={handleSubmit} noValidate>
        <h1>Create your KeyPass account</h1>
        <Alert>{error}</Alert>
        <label className="field">
          Full name
          <input name="full_name" required maxLength={120} value={form.full_name} onChange={handleChange} />
          {fieldErrors.full_name && <span className="small error-text">{fieldErrors.full_name}</span>}
        </label>
        <label className="field">
          Work email
          <input name="email" type="email" required maxLength={254} value={form.email} onChange={handleChange} />
          {fieldErrors.email && <span className="small error-text">{fieldErrors.email}</span>}
        </label>
        <div className="grid-2">
          <label className="field">
            Department
            <select name="department" required value={form.department} onChange={handleChange}>
              <option value="">Select a department</option>
              {Object.keys(DEPARTMENTS).map((department) => (
                <option key={department} value={department}>
                  {department}
                </option>
              ))}
            </select>
            {fieldErrors.department && <span className="small error-text">{fieldErrors.department}</span>}
          </label>
          <label className="field">
            Current role or designation
            <select
              name="designation"
              required
              value={form.designation}
              onChange={handleChange}
              disabled={!form.department}
            >
              <option value="">{form.department ? 'Select a designation' : 'Select a department first'}</option>
              {designations.map((designation) => (
                <option key={designation} value={designation}>
                  {designation}
                </option>
              ))}
            </select>
            {fieldErrors.designation && <span className="small error-text">{fieldErrors.designation}</span>}
          </label>
        </div>
        <label className="field">
          Password (minimum 8 characters)
          <input
            name="password"
            type="password"
            minLength={8}
            maxLength={128}
            autoComplete="new-password"
            required
            value={form.password}
            onChange={handleChange}
          />
        </label>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Creating account...' : 'Create account'}
        </button>
        <p className="small muted">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  )
}
