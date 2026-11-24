import { validateRegistration } from '../accountRules.js'

const valid = {
  full_name: 'Priya Raman',
  email: 'priya@company.com',
  department: 'Finance',
  designation: 'Accountant',
  password: 'StrongPass123',
}

describe('validateRegistration', () => {
  it('accepts a valid registration', () => {
    expect(validateRegistration(valid)).toEqual({})
  })

  it('rejects names with digits, symbols, hyphens or apostrophes', () => {
    for (const full_name of ['@@!!', 'Priya9', 'Mary-Jane', "O'Neil"]) {
      expect(validateRegistration({ ...valid, full_name }).full_name).toBeDefined()
    }
  })

  it('accepts common company domains and rejects malformed emails', () => {
    for (const email of ['a@firm.org', 'b@firm.in', 'c@firm.co.in']) {
      expect(validateRegistration({ ...valid, email }).email).toBeUndefined()
    }
    for (const email of ['sw@12', 'user@keypass', 'user.keypass.com']) {
      expect(validateRegistration({ ...valid, email }).email).toBeDefined()
    }
  })

  it('rejects a designation that does not belong to the department', () => {
    expect(validateRegistration({ ...valid, designation: 'Recruiter' }).designation).toBeDefined()
  })

  it('rejects an unknown department', () => {
    expect(validateRegistration({ ...valid, department: 'Client Delivery' }).department).toBeDefined()
  })
})
