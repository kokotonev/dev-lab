# dev-lab

A personal learning lab for two intertwined goals:

1. **Exploring LLM-powered & agentic software development** — using the Anthropic API to build agents that reason, return structured output, and call tools. This is the part the project is meant to grow into.
2. **Getting hands-on with FastAPI**, with a deliberate focus on **authentication** — cookie-based JWTs, refresh-token rotation, and password hashing done properly.

It's intentionally a sandbox: the code favors clarity and experimentation over production hardening.

## What's inside

```
dev-lab/
├── backend/     # FastAPI app — auth + agent endpoints
└── frontend/    # React + Vite + TypeScript + Tailwind client
```

### Backend (`backend/`)

A FastAPI service built around two routers:

- **`/auth` — authentication** (the main exercise)
  - Register / login / logout
  - **Access tokens**: short-lived (15 min) JWTs (`HS256`, PyJWT), stored in an **HttpOnly cookie**
  - **Refresh tokens**: long-lived (30 days), **rotated on every use**, stored **hashed (SHA-256)** in the database and scoped to the `/auth/refresh` path
  - **Password hashing** with Argon2 via `pwdlib`, including a dummy-hash compare to mitigate user-enumeration timing attacks
  - A provider-aware credential model (`local`, with room for `google` / `github` OAuth later)
  - `token_required` dependency + a custom exception handler for clean 401s

- **`/agent` — LLM & agentic experiments** (the part to grow)
  - `/ask` — conversational chat (authenticated): messages are **persisted to the database** and the full history is replayed to the model on every turn
  - `/get_conversation` — fetch the authenticated user's stored conversation history
  - `/clear_conversation` — wipe the authenticated user's conversation

  Chat history is modelled with `Conversation` and `Message` tables; for now each user has a single conversation, with room to grow into multiple titled threads. A `handle_response` helper inspects the API `stop_reason` (`end_turn`, `max_tokens`, `tool_use`, refusals, …) so tool-use and other flows can be wired in later.


### Frontend (`frontend/`)

A React 19 + Vite + TypeScript SPA (Tailwind CSS, React Router) with login, register, and dashboard pages and an `AuthContext` that talks to the cookie-based backend. The dashboard hosts a **chat UI** wired to the `/agent` endpoints — it loads the stored conversation on mount, optimistically renders sent messages (rolling them back on error), and can clear the conversation.

⚠️ NOTE: The front end was mostly vibe coded, as I still have a very limited knowledge of React (I've gone through the basic parts of the official docs before creating it). 

## Getting started

### Prerequisites

- Python 3.12+ and [`uv`](https://docs.astral.sh/uv/)
- Node.js 20+
- A running PostgreSQL instance
- An `ANTHROPIC_API_KEY` (for the `/agent` endpoints)

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Configure the database connection (see src/database.py) and run migrations
uv run alembic upgrade head

# Set your Anthropic key for the agent endpoints
export ANTHROPIC_API_KEY="sk-ant-..."

# Run the dev server
uv run fastapi dev src/main.py
```

The API serves at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

#### Database migrations (Alembic)

Run the following commands from `backend/`. Models live in `src/models/` and must be imported in `src/models/__init__.py` so Alembic's autogenerate can detect them.

```bash
# After adding or changing a model, generate a migration script
uv run alembic revision --autogenerate -m "describe your change"

# Review the generated file in alembic/versions/, then apply it
uv run alembic upgrade head

# Roll back the most recent migration
uv run alembic downgrade -1

# Inspect history and the current revision
uv run alembic history
uv run alembic current
```

> Autogenerate inspects the live database, so PostgreSQL must be running and reachable (connection string in `alembic.ini`). Always review the generated script before applying it.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The client runs at `http://localhost:5173` (already allow-listed in the backend's CORS config).

## Roadmap / ideas

- Expand the agentic layer: multi-step planning and a real tool-use loop (the `stop_reason` handling is already stubbed for it)
- Support multiple titled conversations per user instead of a single thread
- Wire up OAuth providers (Google, LinkedIn, etc.) using the existing `UserCredential` model

