import {
  daysUntil,
  groupItemsByModule,
  handoverTiming,
  isSafeUrl,
  newItem,
  progressClass,
  todayIso,
} from '../utils.js'

describe('daysUntil and handoverTiming', () => {
  const today = new Date(2026, 10, 24)

  it('counts whole days to the handover date', () => {
    expect(daysUntil('2026-12-04', today)).toBe(10)
  })

  it('describes a passed handover date', () => {
    expect(handoverTiming('2026-11-20', 'Active', today)).toBe('Handover date has passed')
  })

  it('reports signed-off kits as signed off', () => {
    expect(handoverTiming('2026-12-04', 'Completed', today)).toBe('Signed off')
  })

  it('uses singular wording for one day', () => {
    expect(handoverTiming('2026-11-25', 'Active', today)).toBe('1 day to handover')
  })
})

describe('todayIso', () => {
  it('returns a YYYY-MM-DD local date', () => {
    expect(todayIso(new Date(2026, 0, 5, 12))).toBe('2026-01-05')
  })
})

describe('groupItemsByModule', () => {
  it('groups items in display order and drops empty modules', () => {
    const groups = groupItemsByModule([
      { module: 'gotcha', title: 'Watch timezone' },
      { module: 'responsibility', title: 'Weekly report' },
    ])
    expect(groups.map((group) => group.key)).toEqual(['responsibility', 'gotcha'])
    expect(groups[0].items[0].title).toBe('Weekly report')
  })
})

describe('isSafeUrl', () => {
  it('accepts http and https links only', () => {
    expect(isSafeUrl('https://jira.example.test')).toBe(true)
    expect(isSafeUrl('http://intranet.test/page')).toBe(true)
    expect(isSafeUrl('javascript:alert(1)')).toBe(false)
    expect(isSafeUrl('not a url')).toBe(false)
  })
})

describe('progressClass', () => {
  it('maps progress states to badge styles', () => {
    expect(progressClass('Ready to Own')).toBe('badge-done')
    expect(progressClass('Shadowed')).toBe('badge-progress')
    expect(progressClass('Not Started')).toBe('badge-muted')
  })
})

describe('newItem', () => {
  it('creates a blank item with module-specific details', () => {
    const item = newItem('responsibility')
    expect(item.module).toBe('responsibility')
    expect(item.progress).toBe('Not Started')
    expect(item.details.steps).toEqual([])
    expect(item.id).toMatch(/^new-/)
  })
})
