# Market Rank CLI

A small Python CLI that refreshes a US-listed equity ranking shortly after the US market opens, stores the result locally, and displays the top 100 companies with sector-relative valuation, financial-health, and growth metrics.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Optional: install the `market-rank` command as well.
pip install -e .
```

## Use

```bash
# Download the listed US equity universe and calculate a current snapshot.
market-rank update
market-rank update --watchlist # Rank only your watchlist symbols instead of the full universe.
                                # WARNING: this overwrites your current snapshot.

# Faster focused universes: the largest US companies by live market cap.
market-rank update --market-cap 100
market-rank update --market-cap 1000

# Print the current top 100 (or a shorter list).
market-rank top --limit 25
market-rank top --limit all # Displays everything.

# Inspect one company and its sector-relative scores.
market-rank show MSFT

# Keep the process alive; refreshes once on each NYSE trading day at 09:40 ET.
market-rank run

# CRUD watchlist
market-rank watchlist --add symbol
market-rank watchlist --delete symbol
market-rank watchlist --list

# Show your watchlist's scores from the current snapshot.
# Symbols not present in the snapshot (e.g. outside the top 100, or you haven't
# run `update` since adding them) are listed separately instead of causing an error.
market-rank watchlist --top
```

`update` is intentionally explicit: the entire US-listed universe is large and the upstream quote/fundamental endpoints can be slow or rate-limited. The CLI caches company fundamentals for 7 days and uses the most recent daily history for price-based data. On a typical connection, the first full run may take a while.

For an unattended process, run `market-rank run` under your usual service manager (launchd/systemd) or invoke `market-rank update` from a scheduler at 09:40 America/New_York on trading days.

## How scores work

For every metric, the raw comparison is against the **median valid value in the company’s sector**. A score of `1.00` means the sector median. Values above one are better:

- Growth, ROE, asset turnover, cash flow and analyst upside use `company / sector median`.
- PE, forward PE, EV/EBITDA, debt-to-equity and historic PE use `sector median / company` because lower is better.

Negative or zero values are shown as unavailable for ratio-based comparisons where they would be misleading. The composite rank is a winsorized average of available relative scores, plus DCF and analyst-upside contributions; it is a screening signal, not investment advice.

In a particular stock with a lower coverage (specifically below 7), it will take the average score of the industry the stock is registered as. For example:

```bash
        {
      "pe": 1.855066,
      "forward_pe": NaN,
      "historic_pe": 1.8550660309213647,
      "debt_to_equity": NaN,
      "asset_turnover": null,
      "free_cash_flow": NaN,
      "revenue_growth": 0.304,
      "earnings_growth": 0.469,
      "return_on_equity": 0.17789,
      "forward_ev_ebitda": null,
      "dcf_bear": NaN,
      "dcf_base": NaN,
      "dcf_bull": NaN,
      "dcf_upside": NaN,
      "analyst_upside": NaN,
      "symbol": "JPM-PC",
      "name": "JPMorgan Chase & Co.",
      "sector": "Financial Services",
      "industry": "Banks - Diversified",
      "price": 25.01,
      "analyst_target": NaN,
      "score_pe": 7.3754214135777385,
      "score_forward_pe": NaN,
      "score_historic_pe": 7.375421260314379,
      "score_debt_to_equity": NaN,
      "score_asset_turnover": NaN,
      "score_free_cash_flow": NaN,
      "score_revenue_growth": 1.8095238095238093,
      "score_earnings_growth": 1.375366568914956,
      "score_return_on_equity": 1.5884453259913685,
      "score_forward_ev_ebitda": NaN,
      "score_dcf_upside": NaN,
      "score_analyst_upside": NaN,
      "composite_score": 2.554667140886027,
      "coverage": 5
    },
```
The coverage in this particular snippet is only 5 and there are many fundemental points with Nan, or None for the data points. in this particular case, it would take the average of each missing fundemental.

## Data notes

- The stock universe comes from Nasdaq Trader's public `nasdaqlisted.txt` and `otherlisted.txt` directories, filtered to common equity-like listings. ETFs, funds, test issues and non-US symbol formats are excluded.
- Fundamentals, analyst targets, earnings/revenue growth and daily prices are fetched through `yfinance`/Yahoo Finance. Coverage varies by company; missing metrics do not count against a company's composite.
- DCF scenarios use a deliberately transparent five-year FCFE-style projection based on reported free cash flow, revenue/EPS growth forecasts, beta-derived discounting and a Monte Carlo terminal-growth/discount-rate simulation. They are estimates, not analyst models.
- A snapshot always reflects whichever universe was last requested — the full listed universe, a market-cap-limited set, or (with `update --watchlist`) just your watchlist symbols. `market-rank top` and `market-rank watchlist --top` both read from this same snapshot, so scores are only ever comparable within the universe that generated the current snapshot, not across runs made with different `update` options.
