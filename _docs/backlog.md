# Backlog — FairShare

Derived from `_docs/specs.md`. Ordered by dependency: each task builds on the
previous, and the app is working after each milestone.

## Milestone 1 — Django skeleton and models

### Task 1 — Django project and app skeleton
Install Django, create project `fairshare` and app `fairshare_app`. Register
`fairshare_app` in `INSTALLED_APPS` in `fairshare/settings.py`. Add a
`/health/` view returning `{"status": "ok"}`. Confirm
`python manage.py runserver` serves it and `python manage.py test` passes with
one test asserting the health view returns 200.

**Done when:** server starts, health endpoint responds, test suite green.

### Task 2 — Models: Person, Expense, Group
Django models in `fairshare_app/models.py`:
- `Person`: name, created_at
- `Expense`: who_paid (FK to Person), amount, description, created_at
- `ExpenseParticipant`: expense (FK), person (FK), share (computed)
- `Group`: trip_name, people (M2M), expenses (M2M), created_at

All money in `DecimalField(max_digits=10, decimal_places=2)`. Add test fixtures
for a 2-person and 3-person trip.

**Done when:** migrations apply cleanly, models round-trip in tests.

## Milestone 2 — Settlement logic (core algorithm)

### Task 3 — Calculate balances
Service function `calculate_balances(group)` computes per-person balance:
- Paid: sum of expenses where person_paid
- Share: (sum of all expenses) / (number of people) [equally divided for HW2]
- Balance: paid - share

Return dict: `{person_id: balance, ...}`

**Done when:** test with known trip (Alice pays $60 hotel for 3 people, Bob pays
$30 meals for 2 people) produces correct balances.

### Task 4 — Settlement plan (greedy algorithm)
Service function `calculate_settlement(group)` computes minimal transactions:
who pays whom and how much. Greedy: highest creditor receives from highest
debtor first.

Return list of dicts: `[{"from": person_id, "to": person_id, "amount": decimal}, ...]`

**Done when:** test cases:
- 2 people: Alice paid $100, Bob paid $0 → Bob pays Alice $50
- 3 people: Alice paid $90 (for 3), Bob paid $0, Carol paid $0 → Bob and Carol
  each pay Alice $30
- Complex: mixed payments and multiple debtors → produces a correct settlement

## Milestone 3 — Views and templates (frontend)

### Task 5 — Home and group creation view
View: `create_group()` GET/POST. Template: form for trip name and initial people
(comma-separated names). Creates a Group and redirects to group detail.

**Done when:** form accepts input, creates group, redirects to group page.

### Task 6 — Group detail view (dashboard)
View: `group_detail(group_id)` GET. Template: displays people list, expenses
list, balances table, settlement plan. All read-only for now.

**Done when:** all data displays correctly, no errors.

### Task 7 — Add person view
View: `add_person(group_id)` GET/POST. Form: name input. Adds person to group.
Redirects to group detail.

**Done when:** form works, person is added, group detail updates.

### Task 8 — Add expense view
View: `add_expense(group_id)` GET/POST. Form: who_paid (dropdown), amount,
description, people_involved (checkboxes). Adds expense, calculates balances
and settlement. Redirects to group detail.

**Done when:** form works, expense is added, balances and settlement update.

### Task 9 — Styling and UI polish
Add CSS (or use a CSS framework like Bootstrap/Tailwind) for readability.
Make forms and tables look clean. Responsive layout.

**Done when:** UI is usable and looks reasonable on desktop.

## Milestone 4 — Testing and integration

### Task 10 — Unit tests for settlement logic
Test: balance calculation and settlement plan generation. Fixtures for 2-person,
3-person, complex multi-expense trips.

**Done when:** all settlement test cases pass.

### Task 11 — Integration tests (end-to-end)
Test: create group, add people, add expenses, fetch settlement. Use Django's
test client. Verify views and data flow.

**Done when:** end-to-end test covers main happy path.

### Task 12 — Form validation tests
Test: form rejects negative amounts, empty names, invalid input.

**Done when:** invalid input is caught and shown in form errors.

## Milestone 5 — Polish and deployment

### Task 13 — Error handling and user feedback
Add flash messages (Django messages framework) for success/error. Handle edge
cases (empty group, no expenses, etc.).

**Done when:** user gets clear feedback on all actions.

### Task 14 — Write ai-usage-report.md
Reflect: which parts did the AI help with? Where did you override it? What took
longest?

**Done when:** report is written and committed.

### Task 15 — Deploy to Render or Railway
Set up environment variables, database, static files. Deploy app.

**Done when:** app is live at a public URL.

## Backlog tail (Module 3+)

- **Persistent groups and history:** multi-user, groups survive past the trip.
- **Editing and deletion:** allow changes to people and expenses.
- **Payments and receipts:** track actual settlements.
- **Multiple currency:** detect and convert if needed.
- **Shared links:** invite friends without needing an account.
- **Recurring splits:** monthly rent, regular expenses.
- **Authentication:** users own their groups.
