import axios from 'axios'

const TOKEN_KEY = 'keypass.token'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000,
  headers: { 'Content-Type': 'application/json' },
})

export function getStoredToken() {
  try {
    return window.localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function storeToken(token) {
  try {
    window.localStorage.setItem(TOKEN_KEY, token)
  } catch {
    return
  }
}

export function clearToken() {
  try {
    window.localStorage.removeItem(TOKEN_KEY)
  } catch {
    return
  }
}

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLogin = error.config?.url?.includes('/auth/login/')
    if (error.response?.status === 401 && !isLogin) {
      clearToken()
      window.dispatchEvent(new Event('keypass:logout'))
    }
    return Promise.reject(error)
  }
)

export function extractErrorMessage(error) {
  if (error?.response) {
    const message = error.response.data?.error?.message
    return message || `The request failed (HTTP ${error.response.status}).`
  }
  if (error?.code === 'ECONNABORTED') {
    return 'The request timed out. Please try again.'
  }
  return 'Cannot reach the KeyPass server. Check that the backend is running.'
}

export const authApi = {
  register: (payload) => api.post('/auth/register/', payload).then((r) => r.data),
  login: (payload) => api.post('/auth/login/', payload).then((r) => r.data),
  me: () => api.get('/auth/me/').then((r) => r.data),
  directory: () => api.get('/auth/directory/').then((r) => r.data),
}

export const kitApi = {
  list: (role) => api.get('/kits/', { params: { role } }).then((r) => r.data),
  get: (kitId) => api.get(`/kits/${encodeURIComponent(kitId)}/`).then((r) => r.data),
  create: (payload) => api.post('/kits/', payload).then((r) => r.data),
  generatePlaybook: (payload) => api.post('/kits/playbook/generate/', payload).then((r) => r.data),
  updatePlaybook: (kitId, payload) => api.patch(`/kits/${encodeURIComponent(kitId)}/`, payload).then((r) => r.data),
  updateProgress: (kitId, itemId, progress) =>
    api
      .post(`/kits/${encodeURIComponent(kitId)}/items/${encodeURIComponent(itemId)}/progress/`, { progress })
      .then((r) => r.data),
  postMessage: (kitId, itemId, text) =>
    api
      .post(`/kits/${encodeURIComponent(kitId)}/items/${encodeURIComponent(itemId)}/thread/`, { text })
      .then((r) => r.data),
  readinessCheck: (kitId) => api.post(`/kits/${encodeURIComponent(kitId)}/readiness-check/`).then((r) => r.data),
  signOff: (kitId) => api.post(`/kits/${encodeURIComponent(kitId)}/sign-off/`).then((r) => r.data),
}
