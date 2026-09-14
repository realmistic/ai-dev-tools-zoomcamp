# Backlog — FairShare

Derived from `_docs/plan.md`. Ordered by dependency: each task builds on the
previous, and the app is working after each milestone.

## Milestone 1 — API skeleton and models

### Task 1 — FastAPI skeleton and health endpoint
Create a FastAPI app with a `/health/` endpoint returning `{"status": "ok"}`.
Run with `uvicorn` and confirm tests pass.

**Done when:** `uvicorn main:app --reload` serves `/health/` and
`pytest test_health.py` is green.

### Task 2 — Models: Person, Expense, Group
Models in `fairshare_api/models.py`:
- `Person`: name, paid (total paid), owes (total share), balance (paid - owes)
- `Expense`: who_paid (Person), amount, description, people_involved (list of Person)
- `Group`: list of people, list of expenses, metadata (created_at, trip_name)

All money in `Decimal` to the cent. Add test fixtures for a 2-person and 3-person trip.

**Done when:** models instantiate, fixtures round-trip JSON cleanly.

## Milestone 2 — Settlement logic (core algorithm)

### Task 3 — Calculate balances
Given a Group and its expenses, compute per-person balance:
- Paid: sum of expenses where person_paid
- Share: (sum of all expenses) / (number of people) [equally divided for HW2]
- Balance: paid - share

**Done when:** test with known trip (Alice pays $60 hotel for 3 people, Bob pays
$30 meals for 2 people) produces correct balances.

### Task 4 — Settlement plan (greedy algorithm)
Given balances, compute minimal transactions: who pays whom and how much.
Greedy: highest creditor receives from highest debtor first.

**Done when:** test cases:
- 2 people: Alice paid $100, Bob paid $0 → Bob pays Alice $50
- 3 people: Alice paid $90 (for 3), Bob paid $0, Carol paid $0 → Bob and Carol
  each pay Alice $30
- Complex: mixed payments and multiple debtors → produces a correct settlement

### Task 5 — API endpoints for Group operations
POST `/groups/` (create group with name and people)
POST `/groups/{id}/expenses` (add expense)
GET `/groups/{id}` (people, expenses, balances, settlement plan)
GET `/groups/{id}/settlement` (settlement plan only)

**Done when:** endpoints exist, return 200, accept/return correct JSON.

## Milestone 3 — Frontend (React/Next)

### Task 6 — Frontend skeleton
React or Next.js app with a simple layout: header, navigation, empty pages for
"People," "Expenses," "Settlement."

**Done when:** app starts, pages load, no errors.

### Task 7 — People page (add and list)
Form to add a person (name), list of people added. Calls POST `/groups/` and
GET `/groups/{id}`.

**Done when:** add a person, see it in the list, refresh persists.

### Task 8 — Expenses page (add and list)
Form to add an expense (who paid, amount, description, who was involved).
List of expenses. Calls POST `/groups/{id}/expenses`.

**Done when:** add expense, list updates; expense data reaches the API.

### Task 9 — Settlement page
Show balances and settlement plan. Calls GET `/groups/{id}/settlement`.
Clear, readable output: "Bob pays Alice $30."

**Done when:** settlement page shows correct calculation after adding expenses.

## Milestone 4 — OpenAPI and integration tests

### Task 10 — Write OpenAPI contract
Document all endpoints (people, expenses, settlement) in `openapi.yaml` with
request/response schemas. Use it as the contract for both API and frontend.

**Done when:** `openapi.yaml` matches API behavior; API tests pass against it.

### Task 11 — Integration tests (end-to-end)
Test: create group, add people, add expenses, fetch settlement. Verify the
settlement is correct.

**Done when:** test covers the main happy path and known edge cases.

### Task 12 — Frontend component tests
Test: form submission, balance display, settlement rendering.

**Done when:** `npm test` or `pytest` passes.

## Milestone 5 — Polish and deployment

### Task 13 — API documentation and error handling
Add docstrings, validate input (no negative amounts, no duplicate people names),
return sensible 400/422 errors.

**Done when:** `/docs` (Swagger UI) is readable; invalid input is rejected.

### Task 14 — Responsive UI
Ensure frontend works on mobile (if using plain React, add basic media queries;
if using Next.js, leverage built-in responsive defaults).

**Done when:** pages are readable on desktop and mobile.

### Task 15 — Deploy API and frontend
Deploy FastAPI to Render/Railway. Deploy frontend to Vercel or the same platform.

**Done when:** app is live at a public URL.

### Task 16 — Write ai-usage-report.md
Reflect: which parts did the AI help with? Where did you override it? What took
longest?

**Done when:** report is written and committed.

## Backlog tail (Module 3+)

- **Persistent groups and history:** multi-user, groups survive past the trip.
- **Editing and deletion:** allow changes to people and expenses.
- **Payments and receipts:** track actual settlements (Alice venmos Bob $30).
- **Multiple currency:** detect and convert if needed.
- **Shared links:** invite friends to a group without needing an account.
- **Recurring splits:** monthly rent, regular expenses.
- **Authentication:** users own their groups.
- **Postgres and production database:** swap SQLite for production.
