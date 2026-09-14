# FairShare — Product Specification

A lightweight full-stack app to split expenses among friends and settle debts fairly.

Module 2 deliverable for the AI Dev Tools Zoomcamp (2026 cohort).

## The problem

When a group splits a bill — dinner, hotel, trip, groceries — the math is simple
but tracking who paid what and who owes whom is tedious. Splitwise does this
beautifully, but I want to build a version from scratch: minimal scope, clear
API, proper frontend/backend separation, and testable settlement logic.

## Users

**Scenario:** A group of friends on a trip. One person pays for hotel, another
pays for meals, a third covers gas. At the end, we want to know: who paid how
much, who should pay whom, and how much?

Single trip (not multi-user or persistent groups). No authentication. No
real-time collaboration.

## Core features

### F1. Add people

A group starts with a list of people. Add name, initial balance (optional; defaults to 0).

### F2. Record expenses

Add an expense: who paid, amount, and who was involved (subset of the group,
or everyone equally). If Alice paid $60 for hotel and it was for 3 people
(Alice, Bob, Carol), Alice is +$60, the other two are each -$20.

### F3. Calculate balances and settlements

At the end, show:
- Total paid per person
- Share owed per person (total paid divided equally? or weighted? → equal for now)
- Net balance per person (what they paid minus what they owe)
- Minimal settlement plan: "Bob pays Alice $20, Carol pays Alice $40" (not
  "Bob pays Alice $20 and Carol pays Bob $5 and Alice pays Carol...")

### F4. UI: add people, add expense, view balances, view settlement

Four pages. Simple forms and tables. No drag-drop, no real-time, no editing
after the fact. Create and read only.

## Non-goals for Module 2

Deliberately excluded:

- **Persistent groups and history.** This is a trip; it ends. Multi-user
  persistence becomes Module 3.
- **Editing and deletion.** Once an expense is added, it stays.
- **Payments and receipts.** We calculate who owes whom, but don't track
  whether they actually paid.
- **Currency conversion, tax, tips.**
- **Recurring or itemized expenses.**
- **Authentication or sharing links.**

## Technical decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Framework | FastAPI (backend) + React/Next (frontend) | Module 2 requirement; separation of concerns |
| API | OpenAPI contract first | Truth for both frontend and backend, testable |
| Database | SQLite in development | Swap for Postgres in Module 3 |
| Settlement logic | Greedy algorithm | Minimal transactions: highest balance pays/receives first |
| Frontend | React or Next.js | Modern, component-based, easy to test |
| Deployment | Render or Railway | Module 3 scope |

## Repository layout

```text
_docs/plan.md              this specification
_docs/backlog.md           groomed task list
fairshare_api/             FastAPI app (main.py, models, routes)
fairshare_api/tests/       unit tests for API and settlement logic
frontend/                  React app (components, pages, API client)
frontend/tests/            component and integration tests
openapi.yaml               OpenAPI contract (source of truth)
docs/
  ai-usage-report.md       how AI helped (or didn't)
```

## Decision log

1. **Scope.** Considered recurring expenses, multi-trip history, and payment
   tracking. Chose single-trip, create-read-only: the core math problem is
   interesting enough, and anything else is engineering without novelty.
2. **Settlement algorithm.** Greedy (highest balance first) is simple, minimal
   on transactions, and deterministic. Exact optimality is NP-hard; greedy is
   good enough and testable.
3. **Framework pair.** FastAPI for the API (clean, modern, OpenAPI-native),
   React or Next for the frontend (component-based, easy to test). Both are
   standard for Module 2 and make the API/frontend contract visible.

## Acceptance criteria

End of Module 2:
- ✅ OpenAPI contract is written and matches API implementation
- ✅ Settlement logic is tested: known examples (2 people, 3 people, complex
  trip) produce expected settlement plans
- ✅ Frontend forms work: add people, add expense, view settlement
- ✅ API and frontend deployed to a public URL
- ✅ Tests pass: unit (logic), integration (API), and component (frontend)
