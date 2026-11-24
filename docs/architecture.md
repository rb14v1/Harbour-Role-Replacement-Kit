# KeyPass architecture

## Layers

- **Frontend (React, Vite):** pages call `frontend/src/api.js` only. The token lives in `localStorage` under `keypass.token`. A 401 from any non-login call clears it and returns the user to login.
- **Backend (Django REST Framework):** Django is used for routing, settings and the DRF request cycle. No Django ORM models or migrations exist.
- **Data (MongoDB via pymongo):** `core/repositories.py` is the only module that touches collections. Services never build queries.
- **AI (Azure OpenAI via the OpenAI SDK's `AzureOpenAI` client):** `llm/llm_service.py` is the only module that imports `openai`. It calls the endpoint in `AZURE_OPENAI_ENDPOINT`. `OPENAI_MODEL` holds the Azure deployment name.

## Backend modules

| Module | Responsibility |
|---|---|
| `config/` | Settings from environment, root URL conf |
| `core/db.py` | Mongo client, indexes, ping |
| `core/repositories.py` | User and kit collection access |
| `core/security.py` | PBKDF2 password hashing, JWT issue and decode |
| `core/authentication.py` | DRF authentication class for Bearer tokens |
| `core/exceptions.py` | `AppError` and the JSON error handler |
| `accounts/` | Register, login, me, directory. `validation.py` holds the department and designation lists and name and email rules |
| `transitions/services.py` | Kit rules: roles, locking, readiness maths, playbook merge |
| `transitions/presenters.py` | Response shaping per viewer (raw notes shown to owner only) |
| `llm/prompts.py` | Playbook and readiness prompts |
| `llm/llm_service.py` | Azure OpenAI call, JSON parsing, error mapping to `LLMError` |

## Data model

- `users`: `full_name`, `email` (unique), `department`, `designation`, `password_hash`, `created_at`
- `kits`: `title`, `handover_date` (ISO date string), `owner` and `successor` snapshots, `raw_notes` (owner only), `status` (`Active` or `Completed`), `items` (embedded), `last_readiness_brief`, `completed_at`, `completed_by`

Each embedded item holds `id`, `module`, `title`, `details`, `progress` and `thread`. Embedding keeps a kit and its Q&A readable in one read.

## Error handling

Every failure returns `{"error": {"code", "message"}}`. Mongo outages map to 503 `database_unavailable`. OpenAI failures map to the status codes in [api.md](api.md).

## Known limits

- Concurrent edits to the same kit use last-write-wins. Two people editing one item at once can overwrite each other.
- The JWT signing key comes from `SECRET_KEY`. Rotating it logs everyone out.
