import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext.jsx'
import Login from '../pages/Login.jsx'
import { authApi } from '../api.js'

vi.mock('../api.js', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    authApi: {
      ...actual.authApi,
      login: vi.fn(() =>
        Promise.reject({
          response: { status: 401, data: { error: { message: 'Invalid email or password.' } } },
        })
      ),
    },
  }
})

function renderLogin() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('Login page', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('shows the server error message when credentials are rejected', async () => {
    renderLogin()
    await userEvent.type(screen.getByLabelText(/work email/i), 'priya@keypass.demo')
    await userEvent.type(screen.getByLabelText(/password/i), 'wrong-password')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))

    expect(await screen.findByText('Invalid email or password.')).toBeInTheDocument()
    expect(authApi.login).toHaveBeenCalledWith({ email: 'priya@keypass.demo', password: 'wrong-password' })
    await waitFor(() => expect(screen.getByRole('button', { name: /sign in/i })).toBeEnabled())
  })
})
