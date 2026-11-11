# Phase 4 — Top-5 Mega-Cap Rebalancing Dashboard

This is an **educational, simulation-only** Streamlit interface built around the team's Phase 3 Python engine. It does not place brokerage orders.

## MacBook + VS Code setup

1. Install Python 3.11 or 3.12 and VS Code. Open this folder in VS Code.
2. In VS Code choose **Terminal → New Terminal** and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

3. Open the URL shown in the terminal (usually http://localhost:8501).
4. Select **Offline demo (synthetic)** to try the app without internet. Choose **Yahoo Finance** for real historical prices when internet is available.
5. Adjust your current holdings, click **Calculate portfolio and rebalance**, then visit **Run History**.

**Windows:** activate using `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

## How Streamlit works

- `st.title()` adds a page heading.
- `st.sidebar` creates the left navigation and settings panel.
- `st.number_input()` accepts user portfolio amounts.
- `st.button()` triggers calculations.
- `st.plotly_chart()` displays interactive charts.
- `st.dataframe()` displays tables.
- `st.session_state` preserves the last result during UI refreshes.

Edit `app.py`, save it, and Streamlit will offer to rerun the page. You can customize headings, charts, and layouts there.

## Project components

- `app.py`: Streamlit UI, user inputs, allocation and chart views
- `dashboard_logic.py`: connects the UI to the original optimizer and trade-sizing code; deterministic synthetic demo prices
- `dashboard_db.py`: SQLite history for dashboard calculations
- `config.py`, `data_feed.py`, `optimizer.py`, `portfolio_state.py`: **original Phase 3 modules**
- Other Phase 3 modules are retained for reference and command-line usage
- `tests/test_dashboard.py`: simple database and validation tests
- `PHASE3_README.md`: original team documentation

## Run tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```

## Demonstration checklist

1. Show the dashboard and choose offline demo (label the synthetic prices clearly).
2. Display a price chart.
3. Enter a $10,000 simulated portfolio and calculate optimized weights.
4. Explain the 5–40% bounds, 7% cash reserve and 4% drift rule.
5. Display simulated trades and saved SQLite run history.
6. Show unit tests and discuss limitations.
7. If available, repeat with Yahoo Finance data. Do not present synthetic results as real historical performance.

## Safety and limitations

- **No brokerage execution**: the dashboard does not call the Alpaca broker.
- Offline demo data is synthetic, deterministic, and not investment evidence.
- The optimizer may fail for some historical periods; the app shows the error rather than inventing allocations.
- The 5–40% bounds apply to the *invested sleeve* before the 7% cash buffer, so final whole-portfolio stock weights are scaled by 93%.
- Trade sizing is indicative, not cash/settlement/lot-size constrained.
- The dashboard's saved history is separate from the original engine's SQLite audit database.
- The ML forecaster remains disabled for the main strategy because it failed the original validation gate.
- This prototype has not been tested against live market services or brokerage accounts in this build environment.

## Deployment

For a classroom demo, run locally first. Optional Streamlit Community Cloud deployment requires a GitHub repository and a compatible cloud environment. Keep `.env` and API credentials out of GitHub. Avoid deploying the original broker CLI or enabling order execution in the public app.
