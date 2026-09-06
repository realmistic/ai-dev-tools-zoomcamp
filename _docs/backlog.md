# Backlog — Portfolio Lens

Derived from `_docs/plan.md`. Ordered by dependency: each task is small enough
to implement and verify in one sitting, and leaves the app working.

Sample statement for all fixtures: `MULTI_20260101_20260904.pdf`
(IBKR consolidated, 2026-01-01 → 2026-09-04, 79 pages).

## Pre-extracted data and test fixtures

Once Task 3b is done, you can:
- Extract your real MULTI PDF to JSON once: `python manage.py shell_plus` →
  `import_statement(pdf) ; export_to_json(...)`
- Distort for public commit: (a) select a subset of trades (e.g., 10–15 from
  different periods), (b) scale quantities down so total portfolio is ~20k USD,
  (c) rename symbols to different real tickers (must exist in yfinance so
  market data tests pass), (d) keep the structure and trade dates unchanged.
  Example: AMZN → AAPL, NVDA → MSFT, AEIS → TSLA (all real and liquid).
- Commit the sanitized JSON as `data/fixtures/sample-portfolio.json`.
- Tests use the fixture; anyone cloning the repo can verify the app works
  without seeing your portfolio.

## Milestone 1 — Skeleton

### Task 1 — Django project and app skeleton
Install Django, create project `portfolio_lens` and app `portfolio`. Register
`portfolio` in `INSTALLED_APPS` in `portfolio_lens/settings.py`. Add a
`/health/` view returning `{"status": "ok"}`. Confirm
`python manage.py runserver` serves it and `python manage.py test` passes with
one test asserting the health view returns 200.

**Done when:** server starts, health endpoint responds, test suite green.

### Task 2 — Statement models
Models: `Statement` (period start/end, opening NAV, closing NAV, reported TWR,
source filename, uploaded_at), `Instrument` (symbol, description, isin,
exchange, instrument_type, sector, industry), `Position` (statement, instrument,
quantity, cost_price, cost_basis, close_price, value, unrealized_pl),
`Trade` (statement, instrument, account_id, executed_at, quantity, trade_price,
close_price, proceeds, commission, basis, realized_pl, mtm_pl, code),
`CashFlow` (statement, date, kind ∈ deposit/withdrawal/dividend/interest/fee/
commission, amount, instrument nullable).

All money fields `DecimalField(max_digits=18, decimal_places=6)`. Migrate.

**Done when:** migrations apply cleanly, models round-trip in a test.

## Milestone 2 — Ingest and reconcile (F1)

### Task 3a — PDF text extraction
`portfolio/parsing/extract.py`: given a PDF path, return page texts via `pypdf`
and a single normalised document string. Strip page footers
(`Activity Statement - ... Page: N`, `Generated: ...`).

**Done when:** unit test asserts 79 pages extracted and no footer text remains.

### Task 3b — Export parsed sections to JSON
`portfolio/parsing/export_to_json.py`: given a parsed sections dict (from Task
4), serialise it to JSON with a `version` and `exported_at` header. Reverse
function deserialises JSON back to sections dict. This is the format for
`data/fixtures/` and the JSON import endpoint (Task 7b).

**Done when:** round-trip test asserts sections survive dict → JSON → dict
losslessly.

### Task 4 — Section splitter
`portfolio/parsing/sections.py`: a state machine that splits the document into
named sections by their header lines (Account Information, Net Asset Value,
Change in NAV, Mark-to-Market Performance Summary, Realized & Unrealized
Performance Summary, Cash Report, Open Positions, Trades, Dividends,
Deposits & Withdrawals, Financial Instrument Information). Headers repeat on
continuation pages — the splitter must concatenate rather than restart.

**Done when:** test asserts every expected section is found and Trades contains
all rows across its ten page-spans.

### Task 5 — Row parsers
One parser per section, each returning plain dataclasses. Cases that must be
handled, all present in the sample:

- Values as `1,234.56`, `-1,234.56`, `--` for absent
- Descriptions and timestamps wrapped across lines (`2026-08-07,\n12:32:07`)
- Fractional share quantities (`210.7346`, `18.6506`)
- A price split mid-number across a line break (`443.72181818\n2`)
- `Total <SYMBOL>` and `Total Stocks` subtotal rows, which must be captured for
  reconciliation but not stored as trades
- Trade codes `O`, `C`, `C;P`, `P`
- Non-stock blocks (Forex, bond ETFs) tagged by instrument type

**Done when:** parsers produce the expected row count per section, and the
tricky cases above each have a named regression test.

### Task 6 — Import pipeline and reconciliation report
Wire parsers into a `import_statement(path) -> Statement` service. Then
`portfolio/reconcile.py` checks every criterion in F1 of the spec and returns a
report of (check name, expected, actual, delta, pass/fail).

**Done when:** all F1 acceptance criteria pass on the sample statement, as a
test. This is the gate — nothing downstream is built until it is green.

### Task 7 — Import views (PDF and JSON)
Two forms: (a) PDF upload: store under `data/statements/`, extract, parse, and
import. (b) JSON file import: deserialise and import directly. Both converge on
`import_parsed_sections()`. Reconciliation report rendered; failed checks render
red and block analysis.

**Done when:** uploading the sample PDF and importing a JSON-exported version
both produce identical all-green reconciliation reports.

## Milestone 3 — Daily NAV and returns (F2)

### Task 8 — Market data layer
`portfolio/marketdata.py`: `daily_closes(symbols, start, end)` and
`profile(symbol)` (sector, industry) over yfinance, cached in a local table so
reruns are offline. Tests use a recorded fixture, never the live network.

**Done when:** two calls hit the network once; tests pass with no network.

### Task 9 — Holdings replay
Reconstruct daily holdings: seed from Mark-to-Market prior quantities at
2025-12-31, apply trades in timestamp order, carry forward across
non-trading days.

**Done when:** holdings on 2026-09-04 equal the Open Positions section exactly,
symbol by symbol, as a test.

### Task 10 — Daily NAV series
Value daily holdings at closes, apply dated cash flows, and track external
flows separately. Produce a daily series of (market value, cash, NAV,
external flow).

**Done when:** final NAV lands within $1 of `315,800.33`, as a test.

### Task 11 — Period returns
Time-weighted returns from the daily series, chained across external flow days.
Weekly, monthly, YTD. Money-weighted IRR as a secondary figure.

**Done when:** YTD TWR is within 0.5pp of IBKR's `39.46%`; the residual is
asserted and reported.

## Milestone 4 — Benchmark and risk (F3)

### Task 12 — Benchmark comparison
Fetch SPY dividend-adjusted closes for the same window. Compute cumulative and
per-period excess return, plus weeks and months won versus lost.

### Task 13 — Risk metrics
Annualised volatility, Sharpe, maximum drawdown with peak and trough dates,
beta and correlation versus SPY, tracking error.

### Task 14 — Normal deviation profile
Weekly return distribution — median and 5th/25th/75th/95th percentiles — plus a
rolling 20-day volatility band. Flag the current week against that band.

## Milestone 5 — Sectors and export (F4)

### Task 15 — Sector enrichment
Populate `Instrument.sector` and `.industry` from the market data layer.
Weights by sector, industry and position. Top-5 weight and Herfindahl index.

### Task 16 — Contribution analysis
Best and worst contributors by absolute P&L and by return contribution,
reported side by side so a large gain on a small position is visible as such.

### Task 17 — Metrics export
Write every computed metric to `exports/*.json` and `exports/*.csv`, with a
`schema.md` describing each field so Claude Code can query them unaided.

### Task 18 — Dashboard page
One page: NAV curve versus SPY, period return table, risk table, sector
weights, contribution table.

## Backlog tail — Module 2 and beyond

- **Challenger / peer substitution.** For each holding, screen same-industry
  candidates on revenue and EPS growth, debt-to-equity, margin trend and
  upcoming earnings date; rank them and explain why a swap would improve the
  portfolio's risk metrics. The headline Module 2 feature.
- **Position weak-point flags.** Concentration breaches, positions below cost
  with deteriorating fundamentals, earnings-date exposure, crowded sector bets.
- Anthropic tool-calling chat over the verified metric functions.
- Multi-statement history and drift tracking over time.
- Telegram ingestion (forward a PDF, get a report back).
- Docker, Postgres, CI/CD, DigitalOcean deploy (Module 3).
- Authentication, once hosted.
- Alpha Vantage as a second market data provider for fundamentals.
- OpenTelemetry instrumentation and alerting (Module 4).
