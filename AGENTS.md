# AI Agents and Tools Used

## HW1: Portfolio Lens

**Agent:** Claude Code (Anthropic)

**Workflow:**
1. Brainstormed scope with open-ended questions (4 forks recorded in decision log)
2. AI generated initial spec outline; user refined
3. AI created detailed plan.md with acceptance criteria
4. AI generated backlog with dependency ordering
5. User reviewed and approved scope before coding

**Key decisions made by AI:**
- Input format: PDF + pre-extracted JSON
- Data model: Decimal throughout (no float)
- Reconciliation as a hard gate before analytics

**Key decisions made by user:**
- Market data source: yfinance (not Alpha Vantage)
- Benchmark: SPY dividend-adjusted (not price-only)
- Feature 4 (peer screening) deferred to Module 2

## HW2: FairShare

**Agent:** Claude Code (Anthropic)

**Workflow:**
1. Brainstormed project choice from four options (Expense Splitter selected)
2. AI asked clarifying questions on scope (single trip, core features)
3. AI drafted spec and backlog
4. User reviewed scope before coding

**Key decisions made by AI:**
- Settlement algorithm: Greedy (highest balance first)
- Framework split: FastAPI backend + React/Next frontend
- Scope: Create-read-only (no editing)

**Key decisions made by user:**
- Project name: FairShare
- Core workflow: Friends splitting a trip (not recurring)
- Repository: Single repo for all homeworks (not separate)

## Tools and Libraries (to be added during implementation)

- **Backend:** FastAPI, SQLAlchemy, Pydantic, pytest
- **Frontend:** React or Next.js, axios, vitest or jest
- **Database:** SQLite (dev), Postgres (prod)
- **Deployment:** Render or Railway
