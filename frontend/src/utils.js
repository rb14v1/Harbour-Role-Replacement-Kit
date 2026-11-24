export const PROGRESS_STATES = ['Not Started', 'Shadowed', 'Ready to Own']
export const FREQUENCIES = ['Daily', 'Weekly', 'Monthly', 'Ad-hoc']

export const MODULES = [
  { key: 'responsibility', label: 'Recurring Responsibilities' },
  { key: 'access', label: 'Tools, Dashboards & Access' },
  { key: 'stakeholder', label: 'Key Stakeholders & Escalation Contacts' },
  { key: 'gotcha', label: 'Common Gotchas & Unwritten Rules' },
]

export function groupItemsByModule(items = []) {
  return MODULES.map((module) => ({
    ...module,
    items: items.filter((item) => item.module === module.key),
  })).filter((group) => group.items.length > 0)
}

export function daysUntil(isoDate, today = new Date()) {
  const target = new Date(`${isoDate}T00:00:00`)
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  return Math.round((target - start) / 86400000)
}

export function handoverTiming(isoDate, status, today = new Date()) {
  if (status === 'Completed') return 'Signed off'
  const days = daysUntil(isoDate, today)
  if (days < 0) return 'Handover date has passed'
  if (days === 0) return 'Handover is today'
  return `${days} ${days === 1 ? 'day' : 'days'} to handover`
}

export function todayIso(now = new Date()) {
  const offset = now.getTimezoneOffset() * 60000
  return new Date(now - offset).toISOString().slice(0, 10)
}

export function formatDate(isoDate) {
  if (!isoDate) return '-'
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatDateTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}

export function progressClass(progress) {
  if (progress === 'Ready to Own') return 'badge-done'
  if (progress === 'Shadowed') return 'badge-progress'
  return 'badge-muted'
}

export function isSafeUrl(value) {
  try {
    const parsed = new URL(value)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

export function groupByDepartment(people = []) {
  const groups = {}
  for (const person of people) {
    if (!groups[person.department]) groups[person.department] = []
    groups[person.department].push(person)
  }
  return Object.keys(groups)
    .sort((a, b) => a.localeCompare(b))
    .map((department) => ({ department, members: groups[department] }))
}

export function newItem(module) {
  const id = `new-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
  const details = {
    responsibility: { frequency: 'Ad-hoc', steps: [], estimated_minutes: 0 },
    access: { url: '', permission: '' },
    stakeholder: { role: '', contact_when: '' },
    gotcha: { guidance: '' },
  }
  return { id, module, title: '', details: details[module], progress: 'Not Started', thread: [] }
}
