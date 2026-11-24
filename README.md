# KeyPass - Role & Responsibility Transition Kit

KeyPass helps an outgoing owner hand a role to a successor. The owner dumps messy notes, AI builds a structured playbook, the owner reviews it, and the successor works through a readiness checklist. A readiness check before handover gives a gap summary and a sync agenda. Sign-off locks the kit.

Stack: React (Vite) | Django + Django REST Framework | MongoDB (pymongo) | Azure OpenAI (deployment `gpt-5.6-sol` via `OPENAI_MODEL`)

## 1. Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- MongoDB 6 or newer, either through Docker or a local Windows install (no Docker needed)
- An Azure OpenAI key and endpoint (only needed for the AI features; the rest of the app and the tests run without them)

## 2. Start MongoDB

Option A, Docker (PowerShell or bash):

```bash
docker run -d --name keypass-mongo -p 27017:27017 -v keypass-mongo:/data/db mongo:7
```

Option B, Docker Compose (starts Mongo, backend and frontend together, see section 7).

Option C, local install (no Docker): install MongoDB Community Server for Windows. The installer registers a `MongoDB` service that starts automatically and listens on `mongodb://localhost:27017`. Check it under `services.msc` or with `Get-Service MongoDB`.

## 3. Backend (Django)

PowerShell (Windows):

```powershell
cd C:\Users\admin\keypass-transition-kit\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

Open `backend\.env` and set these values:

```
OPENAI_API_KEY=<your Azure OpenAI key>
AZURE_OPENAI_ENDPOINT=https://dev-harbour-open-ai.openai.azure.com
AZURE_OPENAI_API_VERSION=2025-04-01-preview
OPENAI_MODEL=gpt-5.6-sol
```

`OPENAI_MODEL` must be the name of the Azure deployment, not the model family. Change it in `.env` at any time; no code change is needed. Do not put quotes around values.

Then run:

```powershell
python manage.py check
python manage.py test
python seed_data.py
python manage.py runserver 8000
```

bash (macOS or Linux):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py check
python manage.py test
python seed_data.py
python manage.py runserver 8000
```

The API runs at `http://localhost:8000/api`. Health check: `http://localhost:8000/api/health/`.

## 4. Frontend (React)

PowerShell:

```powershell
cd C:\Users\admin\keypass-transition-kit\frontend
copy .env.example .env
npm install
npm test
npm run dev
```

bash:

```bash
cd frontend
cp .env.example .env
npm install
npm test
npm run dev
```

Open `http://localhost:5173`.

## 5. Try the demo workflow

`seed_data.py` creates three employees and one active kit ("Weekly Client Reporting & Sprint Operations") with recurring responsibilities, tool access items, stakeholders, gotchas and sample Q&A.

| Role | Email | Password |
|---|---|---|
| Outgoing owner | priya.raman@keypass.demo | KeyPass@2026 |
| Successor | arjun.mehta@keypass.demo | KeyPass@2026 |
| Other employee | sofia.lindqvist@keypass.demo | KeyPass@2026 |

Registration (`/register`) accepts only these values:

- **Full name:** letters and single spaces. No digits, hyphens or apostrophes.
- **Work email:** `name@domain.tld`, for example `name@company.com`, `.org` or `.in`.
- **Department:** one of the 11 listed in [accounts/validation.py](backend/accounts/validation.py).
- **Designation:** must belong to the selected department.

Suggested walk-through:

1. Log in as Arjun. Open the kit under "Kits I'm Taking Over". Set progress on items, post a question on the Power BI item, and run a readiness check.
2. Log in as Priya. Reply to the open question. Open "Edit playbook" to change an item, then run a readiness check.
3. Create a new kit from "New kit". Enter notes of 20 characters or more and click "Build Structured Playbook". Review the draft, then publish.
4. As the successor, click "Confirm Final Handover Sign-Off". The kit locks.

To reseed, drop the database (`mongosh keypass --eval "db.dropDatabase()"`) and run `python seed_data.py` again. The script refuses to run while demo users exist.

## 6. Tests

| Suite | Command | Needs MongoDB | Needs OpenAI key |
|---|---|---|---|
| Backend (60 tests) | `python manage.py test` (in `backend`) | No (uses mongomock) | No (Azure OpenAI is mocked) |
| Frontend (21 tests) | `npm test` (in `frontend`) | No | No |

## 7. Run everything with Docker Compose

```bash
cp .env.example .env          # then set SECRET_KEY, OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT and OPENAI_MODEL
docker compose up --build
```

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000/api`
- Mongo: `localhost:27017`

Seed the demo data inside the backend container:

```bash
docker compose exec backend python seed_data.py
```

## 8. Configuration reference

Backend (`backend/.env`):

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Django and JWT signing key. Use 32 or more random characters | dev placeholder |
| `DJANGO_DEBUG` | `1` for development, `0` for production | `1` |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Frontend origins allowed to call the API | `http://localhost:5173,http://localhost:8080` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | Database name | `keypass` |
| `MONGO_SERVER_TIMEOUT_MS` | Time before a Mongo outage returns 503 | `3000` |
| `OPENAI_API_KEY` | Azure OpenAI key (the variable name is kept from the earlier setup) | (empty) |
| `AZURE_OPENAI_ENDPOINT` | Resource base URL, for example `https://dev-harbour-open-ai.openai.azure.com`. No path | (empty) |
| `AZURE_OPENAI_API_VERSION` | Azure API version | `2025-04-01-preview` |
| `OPENAI_MODEL` | Azure deployment name, swappable at any time | `gpt-5.6-sol` |
| `OPENAI_TIMEOUT_SECONDS` | Timeout per AI call | `60` |
| `JWT_EXPIRY_HOURS` | Session length | `12` |

Frontend (`frontend/.env`):

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend API base, for example `http://localhost:8000/api` |

## 9. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| "The database is unavailable" | MongoDB is not running. Start it (section 2) and check `MONGO_URI`. |
| "The Azure OpenAI API key is not configured" | Set `OPENAI_API_KEY` in `backend/.env` and restart `runserver`. |
| "The Azure OpenAI endpoint is not configured" | Set `AZURE_OPENAI_ENDPOINT` in `backend/.env` and restart `runserver`. |
| "OpenAI rejected the API key" | The key is wrong, revoked, or belongs to a different resource. |
| "OpenAI returned an error (HTTP 502)" | Usually `OPENAI_MODEL` is not an existing deployment name (`DeploymentNotFound`). Check the name in Azure. The app does not substitute one. |
| Browser shows "access denied" on the endpoint URL | Expected. The API needs an `api-key` header, which a browser does not send. Test with a POST request that sends the `api-key` header, for example with `Invoke-RestMethod` in PowerShell. |
| "Cannot reach the KeyPass server" in the UI | The backend is not running on port 8000, or `VITE_API_BASE_URL` is wrong. Restart `npm run dev` after editing `.env`. |
| CORS error in the browser console | Add the frontend origin to `CORS_ALLOWED_ORIGINS`. |

## 10. Readiness percentage

Each item counts 0 for `Not Started`, 0.5 for `Shadowed` and 1 for `Ready to Own`. The kit percentage is the average across items. Reference: [docs/api.md](docs/api.md) and [docs/architecture.md](docs/architecture.md).
