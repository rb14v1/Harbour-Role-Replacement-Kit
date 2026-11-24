import re

DEPARTMENTS = {
    "Software": ["Software Engineer", "Senior Software Engineer", "Software Architect", "Tech Lead"],
    "Communication": ["Communications Specialist", "Content Writer", "PR Manager", "Internal Communications Lead"],
    "Design": ["UX Designer", "UI Designer", "Visual Designer", "Design Lead"],
    "Engineering": ["Frontend Engineer", "Backend Engineer", "Full Stack Engineer", "Test Engineer", "Engineering Manager"],
    "Finance": ["Financial Analyst", "Accountant", "Payroll Specialist", "Finance Manager"],
    "Human Resources": ["HR Generalist", "Recruiter", "HR Business Partner", "Talent Acquisition Lead"],
    "Learning & Development": ["Trainer", "Instructional Designer", "L&D Specialist", "L&D Manager"],
    "Marketing": ["Marketing Executive", "Digital Marketing Specialist", "Brand Manager", "Marketing Manager"],
    "Product Management": ["Product Manager", "Senior Product Manager", "Product Owner", "Product Analyst"],
    "Support": ["Support Agent", "Support Engineer", "Support Team Lead", "Customer Success Manager"],
    "Business Analysis": ["Business Analyst", "Senior Business Analyst", "Data Analyst", "Process Analyst"],
}

NAME_PATTERN = r"^[A-Za-z]+(?: [A-Za-z]+)*$"
EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,6}$"

NAME_ERROR = "Full name can contain only letters and single spaces."
EMAIL_ERROR = "Enter a valid work email, for example name@company.com."
DESIGNATION_ERROR = "Choose a designation from the selected department."

_NAME_RE = re.compile(NAME_PATTERN)
_EMAIL_RE = re.compile(EMAIL_PATTERN)


def is_valid_name(value):
    return bool(_NAME_RE.fullmatch(value or ""))


def is_valid_email(value):
    return bool(_EMAIL_RE.fullmatch(value or ""))
