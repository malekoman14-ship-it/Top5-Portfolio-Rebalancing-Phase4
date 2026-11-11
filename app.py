"""Phase 4 Streamlit dashboard. Educational simulation only: NEVER sends orders."""
import json
import pandas as pd
import plotly.express as px
import streamlit as st

import config
from dashboard_db import get_runs, save_run
from dashboard_logic import calculate, example_prices

st.set_page_config(page_title='Top-5 Rebalancing Engine', page_icon='📈', layout='wide')
st.title('📈 Top-5 Mega-Cap Rebalancing Engine')
st.caption('Phase 4 • Educational portfolio analytics • SIMULATION ONLY — no brokerage orders are submitted')

with st.sidebar:
    st.header('Dashboard settings')
    page = st.radio('Navigate', ['Overview & Rebalance', 'Run History', 'About & Methodology'])
    mode = st.radio('Market data', ['Offline demo (synthetic)', 'Yahoo Finance (historical)'])
    capital = st.number_input('Portfolio value (USD)', min_value=1000.0, value=10000.0, step=1000.0)
    st.info('This application never connects to a broker or submits orders.')

if page == 'Overview & Rebalance':
    st.subheader('1. Market data')
    @st.cache_data(ttl=900, show_spinner=False)
    def load_market_data(selected):
        if selected.startswith('Offline'):
            return example_prices(config.LOOKBACK_DAYS), 'Synthetic demonstration data'
        from data_feed import get_price_history
        return get_price_history(config.TICKERS, config.LOOKBACK_DAYS), 'Yahoo Finance adjusted historical closes'

    try:
        prices, source_label = load_market_data(mode)
        st.success(f'Data loaded: {source_label} • {len(prices)} trading days • through {prices.index[-1].date()}')
        selected = st.selectbox('Stock price chart', config.TICKERS)
        st.line_chart(prices[selected].rename('Price (USD)'))
        st.caption('Offline demo uses generated prices. It is not actual market history and must not be reported as real backtest performance.')
    except Exception as exc:
        st.error(f'Unable to load market data: {exc}')
        st.stop()

    st.subheader('2. Enter your current allocation')
    st.caption('Percent of your portfolio in each stock. The remaining percentage is cash.')
    default = {t: 18.6 for t in config.TICKERS}  # 93% stocks + 7% cash
    cols = st.columns(5)
    current_pct = {}
    for i,t in enumerate(config.TICKERS):
        with cols[i]:
            current_pct[t] = st.number_input(f'{t} %', min_value=0.0, max_value=100.0,
                                              value=default[t], step=1.0, key=f'pct_{t}')
    cash_pct = 100 - sum(current_pct.values())
    if cash_pct < -0.001:
        st.error('Stock allocations exceed 100%. Reduce them before calculating.')
        st.stop()
    st.metric('Remaining cash allocation', f'{cash_pct:.1f}%')
    st.caption('These are simulated holdings entered by you, not broker-reported positions.')

    if st.button('Calculate portfolio and rebalance', type='primary'):
        try:
            result = calculate(prices, capital, current_pct, cash_pct)
            st.session_state['result'] = result
            st.session_state['run_mode'] = mode
            st.session_state['run_capital'] = capital
            save_run(mode, capital, result['targets'], result['current'],
                     result['drift'], result['trades'])
            st.success('Calculation completed and saved to SQLite.')
        except Exception as exc:
            st.error(f'Calculation failed: {exc}')
            st.info('Check that the required packages are installed and try again.')

    if 'result' in st.session_state:
        result = st.session_state['result']
        st.subheader('3. Optimized allocation')
        df = pd.DataFrame({'Asset': list(result['targets']),
                           'Target %': [100*v for v in result['targets'].values()]})
        left, right = st.columns([1,1])
        with left:
            st.plotly_chart(px.pie(df, names='Asset', values='Target %', hole=.38,
                                   title='Recommended portfolio weights'), use_container_width=True)
        with right:
            st.dataframe(df.style.format({'Target %':'{:.2f}%'}), hide_index=True, use_container_width=True)
            st.metric('Drift gate', 'Triggered' if result['needs_rebalance'] else 'Not triggered')
            st.caption('The optimizer applies 5–40% bounds to the invested-stock weights, then reserves 7% cash.')
        st.subheader('4. Proposed trades — simulation only')
        if result['trades']:
            st.dataframe(pd.DataFrame(result['trades']), hide_index=True, use_container_width=True)
        else:
            st.info('No proposed trades: the 4-percentage-point drift threshold was not exceeded, or there were no eligible orders.')
        st.warning('These are theoretical trade instructions. No orders were submitted. Proposed buys and sells do not model all execution constraints or guarantee a 7% cash balance after fills.')

elif page == 'Run History':
    st.subheader('Saved dashboard runs')
    runs = get_runs()
    if not runs:
        st.info('No saved runs yet. Calculate an allocation on the Overview page.')
    else:
        for run in runs:
            run_id, ts, run_mode, run_capital, targets, current, drift, trades = run
            with st.expander(f'Run #{run_id} • {ts} • ${run_capital:,.2f} • {run_mode}'):
                st.json({'targets':json.loads(targets), 'current':json.loads(current),
                         'drift':json.loads(drift), 'proposed_trades':json.loads(trades)})

else:
    st.subheader('System architecture and limitations')
    st.markdown('''**Pipeline:** price data → historical-mean expected returns → Ledoit-Wolf covariance
    → maximum-Sharpe portfolio optimization → 7% cash reserve → current-versus-target
    drift check → simulated trade list → SQLite audit log.

    **Original Phase 3 modules reused:** `config.py`, `data_feed.py`, `optimizer.py`,
    and `portfolio_state.py`. `dashboard_logic.py` provides the interface adapter.

    **ML status:** Ridge and LightGBM are experimental and intentionally NOT used
    for the main recommendation because the Phase 3 validation gate did not pass.

    **Safety:** This dashboard does not invoke `broker_alpaca.py`, submit any
    orders, or access live brokerage accounts. Offline data is synthetic.
    The simulated position quantities may be fractional and the order list is
    an estimate, not an executable trading plan.''')
