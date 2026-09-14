# ai-dev-tools-zoomcamp

Coursework for the AI Dev Tools Zoomcamp 2026 cohort.

## FairShare (HW2)

A lightweight full-stack app to split expenses among friends and settle debts fairly.

**The idea:** A group on a trip. One person pays for the hotel, another for meals, a third for gas. At the end, calculate who paid what, who owes whom, and the minimal settlement plan.

**Features:**
- Add people and expenses
- Calculate per-person balances (paid vs. owed)
- Generate a minimal settlement plan (greedy algorithm)
- FastAPI backend + React/Next frontend
- OpenAPI contract as the source of truth

See `_docs/plan.md` for the full specification and `_docs/backlog.md` for the task list.

## Setup

```bash
# Install dependencies
uv sync

# Start the FastAPI backend
uv run uvicorn fairshare_api.main:app --reload

# In another terminal, start the frontend
cd frontend
npm install
npm run dev
```

Backend runs at `http://127.0.0.1:8000` | Frontend at `http://127.0.0.1:3000`

API docs (Swagger) at `http://127.0.0.1:8000/docs`

## Testing

```bash
# Backend tests
uv run pytest fairshare_api/tests/

# Frontend tests (if using vitest or jest)
cd frontend && npm test
```

## Commands (quick reference)

| Command | What it does |
| --- | --- |
| `uv sync` | Install/sync dependencies |
| `uv run uvicorn fairshare_api.main:app --reload` | Start FastAPI server |
| `cd frontend && npm run dev` | Start frontend dev server |
| `uv run pytest fairshare_api/tests/` | Run backend tests |
| `cd frontend && npm test` | Run frontend tests |

## Project structure

```
_docs/                 specification and backlog
fairshare_api/         FastAPI app (main.py, models, routes)
fairshare_api/tests/   unit tests
frontend/              React/Next.js app
frontend/tests/        component tests
openapi.yaml           API contract
docs/
  ai-usage-report.md   how AI helped
```

---

**Status:** Module 2 in progress. Building Tasks 1–5 (API skeleton, settlement logic, basic endpoints).
