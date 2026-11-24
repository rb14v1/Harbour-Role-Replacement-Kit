export const DEPARTMENTS = {
  Software: ['Software Engineer', 'Senior Software Engineer', 'Software Architect', 'Tech Lead'],
  Communication: ['Communications Specialist', 'Content Writer', 'PR Manager', 'Internal Communications Lead'],
  Design: ['UX Designer', 'UI Designer', 'Visual Designer', 'Design Lead'],
  Engineering: ['Frontend Engineer', 'Backend Engineer', 'Full Stack Engineer', 'Test Engineer', 'Engineering Manager'],
  Finance: ['Financial Analyst', 'Accountant', 'Payroll Specialist', 'Finance Manager'],
  'Human Resources': ['HR Generalist', 'Recruiter', 'HR Business Partner', 'Talent Acquisition Lead'],
  'Learning & Development': ['Trainer', 'Instructional Designer', 'L&D Specialist', 'L&D Manager'],
  Marketing: ['Marketing Executive', 'Digital Marketing Specialist', 'Brand Manager', 'Marketing Manager'],
  'Product Management': ['Product Manager', 'Senior Product Manager', 'Product Owner', 'Product Analyst'],
  Support: ['Support Agent', 'Support Engineer', 'Support Team Lead', 'Customer Success Manager'],
  'Business Analysis': ['Business Analyst', 'Senior Business Analyst', 'Data Analyst', 'Process Analyst'],
}

const NAME_RE = /^[A-Za-z]+(?: [A-Za-z]+)*$/
const EMAIL_RE = /^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,6}$/

export const NAME_ERROR = 'Full name can contain only letters and single spaces.'
export const EMAIL_ERROR = 'Enter a valid work email, for example name@company.com.'
export const DEPARTMENT_ERROR = 'Choose a department from the list.'
export const DESIGNATION_ERROR = 'Choose a designation from the selected department.'

export function validateRegistration(form) {
  const errors = {}
  const name = form.full_name.trim()
  const email = form.email.trim()
  const department = form.department.trim()
  const designation = form.designation.trim()

  if (!NAME_RE.test(name)) errors.full_name = NAME_ERROR
  if (!EMAIL_RE.test(email)) errors.email = EMAIL_ERROR
  if (!Object.prototype.hasOwnProperty.call(DEPARTMENTS, department)) {
    errors.department = DEPARTMENT_ERROR
  } else if (!DEPARTMENTS[department].includes(designation)) {
    errors.designation = DESIGNATION_ERROR
  }
  return errors
}
