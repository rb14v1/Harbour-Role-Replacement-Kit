# KeyPass API

Base URL: `http://localhost:8000/api`. All routes except register, login and health require `Authorization: Bearer <token>`.

Errors use one shape: `{"error": {"code": "...", "message": "...", "details": {...}}}`.

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/health/` | Public | Database reachability check |
| POST | `/auth/register/` | Public | Create account, returns token and user |
| POST | `/auth/login/` | Public | Log in, returns token and user |
| GET | `/auth/me/` | Any user | Current user |
| GET | `/auth/directory/` | Any user | All other employees, for successor selection |
| GET | `/kits/?role=owner\|successor` | Any user | Kits the user hands over, or takes over |
| POST | `/kits/` | Owner | Publish a reviewed kit with items |
| POST | `/kits/playbook/generate/` | Any user | AI draft of playbook items from raw notes (not saved) |
| GET | `/kits/{id}/` | Owner or successor | Kit detail with items, threads and permissions |
| PATCH | `/kits/{id}/` | Owner, while Active | Edit title, handover date or items. Existing progress and threads are kept |
| POST | `/kits/{id}/items/{item_id}/progress/` | Successor, while Active | Set `Not Started`, `Shadowed` or `Ready to Own` |
| POST | `/kits/{id}/items/{item_id}/thread/` | Owner or successor | Post a question or reply (allowed after sign-off) |
| POST | `/kits/{id}/readiness-check/` | Owner or successor | AI readiness brief, stored on the kit |
| POST | `/kits/{id}/sign-off/` | Owner or successor, while Active | Lock kit as `Completed` with timestamp |

## Registration rules

`POST /auth/register/` returns 400 with `details` keyed by field when:

- `full_name` contains anything other than letters and single spaces.
- `email` is not `name@domain.tld` with a 2 to 6 letter ending.
- `department` is not one of the 11 values in `accounts/validation.py`.
- `designation` does not belong to the chosen department.

## Readiness percentage

Each item contributes 0 for `Not Started`, 0.5 for `Shadowed` and 1 for `Ready to Own`. The kit percentage is the average across all items, rounded to a whole number.

## Status codes

| Code | Meaning |
|---|---|
| 400 | Validation failed or business rule breached (self-handover, past date, unknown successor) |
| 401 | Missing, invalid or expired token; wrong login credentials |
| 403 | Authenticated but not permitted for this action or kit |
| 404 | Kit or item not found |
| 409 | Email already registered, or kit is completed and locked |
| 422 | Strict playbook item validation failed |
| 429 | OpenAI rate limit |
| 502 | OpenAI returned an unusable response |
| 503 | Database unavailable, OpenAI key missing or rejected, or OpenAI unreachable |
| 504 | OpenAI timed out |
