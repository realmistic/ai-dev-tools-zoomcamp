# ai-dev-tools-zoomcamp

Coursework for the AI Dev Tools Zoomcamp 2026 cohort.

## Portfolio Lens (HW1)

A Django app that turns Interactive Brokers Activity Statement PDFs into trustworthy portfolio analytics and performance metrics.

**The idea:** Parse broker statements into a reconciled data model, reconstruct daily performance, benchmark against S&P 500, and export verified metrics so a coding agent (Claude Code) can answer open questions about the portfolio without guessing from a PDF.

**Features:**
- Ingest and reconcile IBKR PDFs (acceptance tests on NAV, TWR, P&L)
- Reconstruct daily NAV curve from trade log; time-weighted returns by period
- Benchmark vs SPY; risk metrics (volatility, Sharpe, drawdown, beta)
- Sector weights and contribution analysis; JSON/CSV export

See `_docs/plan.md` for the full specification and `_docs/backlog.md` for the task list.

## Setup

```bash
# Install dependencies
uv sync

# Create and run migrations
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
```

Visit `http://127.0.0.1:8000/health/` to verify the server is running.

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
portfolio_lens/        Django project (settings, urls, wsgi)
portfolio/             Django app (models, parsing, analytics, views)
portfolio/tests/       unit and reconciliation tests
data/
  statements/          uploaded PDFs (gitignored)
  fixtures/            test data (sanitized JSON)
exports/               generated metrics (gitignored)
```

---

**Status:** Module 1 scope locked. Building Tasks 1–7 (ingest, reconcile, daily NAV).
