# ai-dev-tools-zoomcamp

Coursework for the AI Dev Tools Zoomcamp 2026 cohort.

## FairShare (HW2)

A Django app to split expenses among friends and settle debts fairly.

**The idea:** A group on a trip. One person pays for the hotel, another for meals, a third for gas. At the end, calculate who paid what, who owes whom, and the minimal settlement plan.

**Features:**
- Add people and expenses
- Calculate per-person balances (paid vs. owed)
- Generate a minimal settlement plan (greedy algorithm)
- Django full-stack (templates + views)

See `_docs/specs.md` for the full specification and `_docs/backlog.md` for the task list.

## Setup

```bash
# Install dependencies
uv sync

# Create and run migrations
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the app.

## Testing

```bash
# Run all tests
uv run python manage.py test

# Run tests with verbose output
uv run python manage.py test --verbosity=2
```

## Commands (quick reference)

| Command | What it does |
| --- | --- |
| `uv sync` | Install/sync dependencies |
| `uv run python manage.py migrate` | Apply database migrations |
| `uv run python manage.py runserver` | Start dev server (port 8000) |
| `uv run python manage.py test` | Run test suite |
| `uv run python manage.py shell` | Interactive Python shell with Django context |

## Project structure

```
_docs/                 specification and backlog
fairshare/             Django project (settings, urls, wsgi)
fairshare_app/         Django app (models, views, forms, templates)
fairshare_app/tests/   tests
fairshare_app/templates/ HTML templates
static/                CSS, JavaScript
```

---

**Status:** HW2 in progress. Building Tasks 1–4 (Django skeleton, models, settlement logic, views).
