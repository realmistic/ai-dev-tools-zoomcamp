# Portfolio Lens — Product Specification

A local Django app that turns an Interactive Brokers Activity Statement into a
trustworthy set of portfolio metrics, so that a coding agent (Claude Code) can
answer open questions about the portfolio against verified numbers instead of
guessing from a PDF.

Module 1 deliverable for the AI Dev Tools Zoomcamp (2026 cohort).

## The problem

I run a mostly-stock portfolio at IBKR across three sub-accounts. My thesis is:

1. Don't lose money.
2. Outperform the S&P 500.
3. Know what normal deviation looks like for *my* portfolio, so a bad week is
   recognisable as noise or as damage.
4. Improve risk metrics by marginal substitution — swap a weak position for a
   better one in the same vertical, not by restructuring everything.

Today the only artifact I have is an 79-page PDF activity statement. It contains
excellent data and answers none of those questions directly. Anything I want to
know requires manual arithmetic, and manual arithmetic is where I stop asking.

## Users

Single user (me), running locally. No authentication, no multi-tenancy. If the
app is later hosted (Module 3), auth becomes a prerequisite and is tracked in
the backlog, not here.

## Core features (Module 1 scope)

These four form one dependency chain. Each is only trustworthy if the one above
it is.

### F1. Ingest and reconcile

Upload an IBKR Activity Statement PDF. Parse it into Django models and prove
the parse is correct by reconciling against the statement's own totals.

Sections parsed:

| Section | Gives us |
| --- | --- |
| Account Information | account ids, base currency, period |
| Net Asset Value | opening and closing NAV |
| Change in NAV | deposits, dividends, interest, fees, commissions, IBKR's TWR |
| Mark-to-Market Performance Summary | prior/current quantity and price per symbol |
| Realized & Unrealized Performance Summary | realized vs unrealized, short-term vs long-term |
| Open Positions | quantity, cost basis, close price, value, unrealized P/L |
| Trades | per-execution date/time, quantity, price, proceeds, commission, realized P/L, open/close code |
| Deposits & Withdrawals | external cash flows, dated |
| Dividends | dated income per symbol |
| Financial Instrument Information | description, ISIN, exchange, instrument type (COMMON / ETF / REIT) |

**Acceptance criteria** — the parse is accepted only if, for the sample
statement `MULTI_20260101_20260904.pdf`:

- Sum of Open Positions value equals closing Stock NAV `315,443.14` (± $1)
- Closing NAV equals `315,800.33` (± $1)
- Total P/L for statement period equals `83,852.95` (± $1)
- Deposits & Withdrawals sum to `37,000.00` (± $1)
- Prior quantity × prior price, summed, equals opening Stock NAV `194,715.61` (± 0.5%)
- Per-symbol realized + unrealized equals the statement's per-symbol total for
  every symbol

Reconciliation failures are surfaced in the UI as a data-quality report, not
swallowed. A statement that does not reconcile is not analysed.

### F2. Daily NAV curve and period returns

Reconstruct a daily equity curve from 2025-12-31 forward:

- Opening positions come from Mark-to-Market prior quantities.
- The Trades log is replayed in timestamp order to maintain daily holdings.
- Daily holdings are valued at yfinance daily closes.
- Dividends, interest, fees and commissions are applied on their dated rows.
- External cash flows (deposits/withdrawals) are recorded separately so they
  never appear as performance.

From that single series, derive:

- Weekly, monthly and YTD returns, time-weighted so the 37k of deposits does
  not flatter or penalise the result
- Money-weighted return (IRR) as a secondary figure, since it reflects what my
  cash actually earned
- Cumulative return curve

**Acceptance criteria:** reconstructed YTD time-weighted return matches IBKR's
reported `39.46%` within 0.5 percentage points. The residual is reported, not
hidden — it is the honest measure of how good the reconstruction is.

### F3. Benchmark and risk metrics

Answer "am I actually beating the index, and what is normal for me?".

- **Benchmark:** SPY total return (dividend-adjusted closes), because portfolio
  returns include dividends and a price-only index would be an unfair
  comparison. `^GSPC` price return shown as a secondary reference.
- **Relative performance:** cumulative and per-period excess return; count of
  weeks and months won versus lost.
- **Risk:** annualised volatility, Sharpe ratio, maximum drawdown with peak and
  trough dates, beta and correlation versus SPY, tracking error.
- **Normal deviation:** the empirical distribution of my weekly returns —
  median, 5th/25th/75th/95th percentiles, and a rolling 20-day volatility band.
  This is the feature that makes a bad week interpretable.

### F4. Sector map and metrics export

- Sector and industry per holding from yfinance, cached locally so a rebuild
  does not re-hit the network.
- Weights by sector, industry and position; concentration measures
  (top-5 weight, Herfindahl index).
- Best and worst contributors to P&L in absolute dollars and as return
  contribution — the distinction matters, because a 40% gain on a 1% position
  is not a good outcome.
- Export every computed metric to `exports/*.json` and `exports/*.csv`.

The export is what makes feature 3 of my original list — "answer additional
questions from the chat" — work today: Claude Code reads the exports and does
ad-hoc analysis against verified numbers. No LLM runs inside the app, so there
is no API key in the codebase and no risk of a model inventing arithmetic.

## Non-goals for Module 1

Deliberately excluded, with the reason:

- **The challenger / peer-substitution feature.** My fourth original feature —
  find same-sector stocks with better revenue and EPS growth, less debt, good
  recent news, upcoming earnings. It is the most interesting feature and the
  one most likely to consume the whole evening, and it is worthless if built on
  numbers that do not reconcile. It stays in the backlog tail as the Module 2
  headline feature.
- **LLM inside the application.** Deferred until there is a hosted surface
  worth putting it behind.
- **Telegram ingestion and hosting.** Module 3 territory.
- **Forex P&L and securities-lending income modelling.** Present in the
  statement but tiny (-$30.81 forex, small lending fees). Parsed and stored,
  excluded from performance attribution.
- **Tax lots, wash sales, tax optimisation.**
- **Options, futures, real-time quotes, intraday marks.**
- **Multi-user access and authentication.**

## Technical decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Framework | Django + SQLite | Module 1 requirement; SQLite swaps for Postgres in Module 3 |
| PDF parsing | `pypdf` text extraction plus a section state machine | Layout is stable and text-based; verified working against the sample |
| Input formats | PDF upload or pre-extracted JSON import | JSON exports the parser output; reusable for testing and commitable as a sanitized fixture |
| Market data | `yfinance` | No API key, no meaningful rate limit, provides sector, industry, adjusted closes and fundamentals in one dependency |
| Data access | Provider functions behind a thin module boundary | Alpha Vantage can be added later without touching analytics code |
| Accounts | Consolidated into one portfolio, `account_id` retained per trade | The statement is already consolidated; per-account views are a later cut |
| Money | `Decimal` throughout, never `float` | Reconciliation to the cent is an acceptance criterion |
| Q&A | Claude Code against `exports/` | Zero cost, no key, agent can write ad-hoc analysis |

## Repository layout

```text
_docs/plan.md          this specification
_docs/backlog.md       groomed task list
portfolio_lens/        Django project (settings, urls, wsgi)
portfolio/             Django app: models, parser, analytics, views
portfolio/tests/       unit and reconciliation tests
exports/               generated metrics, gitignored
data/
  statements/          uploaded PDFs, gitignored
  fixtures/            pre-extracted test data (sanitized JSON), committed
```

## Decision log

The scope above came from a bounded brainstorm. Recording the forks, because
the discarded options explain the shape of the result.

1. **Interface.** Considered a local CLI, a Telegram bot, a web dashboard and a
   scheduled report. Chose a Django web app, since the course mandates Django
   in Module 1 and containerised hosting in Module 3. Telegram deferred rather
   than dropped.
2. **Input data.** Rather than guess at the schema, I pointed the agent at a
   real statement. It turned out to be far richer than expected — a full trades
   log with open/close codes and an IBKR-computed TWR — which upgraded feature
   F2 from "estimate" to "reconstruct and verify".
3. **Market data.** Considered Alpha Vantage, since working code already exists
   in `snp500-alphavantage`. Rejected for now: the free tier is 25 requests a
   day and this portfolio holds roughly 70 symbols. yfinance has no such limit.
4. **Time series.** Considered storing one statement snapshot per period and
   diffing them, which would be trivially correct but would start history at
   zero today. Chose reconstruction from the trade log instead: it recovers the
   whole year immediately, and IBKR's own NAV and TWR figures serve as the test
   oracle that keeps the reconstruction honest.
5. **AI layer.** Considered Anthropic tool-calling inside Django. Deferred:
   deterministic metrics plus Claude Code gives the same answers tonight with
   no API key, no token cost and no possibility of a model doing the arithmetic
   itself.
