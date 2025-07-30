import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PRM.US Financial Overview", layout="centered")

st.title("📊 PRM.US Financial Metrics Dashboard")

# Load API key securely
api_key = st.secrets["EODHD_API_KEY"]

ticker = "PRM.US"

def get_fundamental_data(ticker, api_key, section):
    url = f"https://eodhd.com/api/fundamentals/{ticker}?api_token={api_key}&fmt=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get(section, {})
    else:
        return {}

# Retrieve necessary data
general = get_fundamental_data(ticker, api_key, "General")
highlights = get_fundamental_data(ticker, api_key, "Highlights")
valuation = get_fundamental_data(ticker, api_key, "Valuation")
ratios = get_fundamental_data(ticker, api_key, "Financials::Metrics")
balance_sheet = get_fundamental_data(ticker, api_key, "Financials::Balance_Sheet::quarterly")
cashflow = get_fundamental_data(ticker, api_key, "Financials::Cash_Flow::quarterly")
income = get_fundamental_data(ticker, api_key, "Financials::Income_Statement::quarterly")

# Get Q1 2025 data (most recent)
quarter = "2025-03-31"
bs_q = balance_sheet.get(quarter, {})
cf_q = cashflow.get(quarter, {})
inc_q = income.get(quarter, {})

# Extract and calculate values
market_cap = highlights.get("MarketCapitalization")
ev = valuation.get("EnterpriseValue")
fcf = cf_q.get("freeCashFlow")
ev_fcf = ev / fcf if ev and fcf else None
pb = valuation.get("PriceBookMRQ")
pe = highlights.get("PERatio")
eps = highlights.get("EarningsShare")
ev_ebitda = valuation.get("EnterpriseValueEbitda")
roe = highlights.get("ReturnOnEquityTTM")
roa = highlights.get("ReturnOnAssetsTTM")
industry = general.get("Industry")
sector = general.get("Sector")
description = general.get("Description")
revenue = inc_q.get("totalRevenue")
gross_profit = inc_q.get("grossProfit")
total_debt = bs_q.get("totalDebt")
total_equity = bs_q.get("totalStockholdersEquity")
de_ratio = total_debt / total_equity if total_debt and total_equity else None
ttm_net_income = highlights.get("NetIncomeTTM")
ttm_invested_capital = bs_q.get("totalAssets") - bs_q.get("totalCurrentLiabilities") if bs_q.get("totalAssets") and bs_q.get("totalCurrentLiabilities") else None
roic = (ttm_net_income / ttm_invested_capital) * 100 if ttm_net_income and ttm_invested_capital else None
peg_trailing = pe / highlights["EPSGrowthTTM"] if pe and highlights.get("EPSGrowthTTM") else None
peg_forward = pe / highlights["EPSGrowthNext5Y"] if pe and highlights.get("EPSGrowthNext5Y") else None

# Assemble DataFrame
data = {
    "Metric": [
        "Ticker", "Data's Date", "Industry", "Sector", "Description",
        "P/E", "P/B", "FCF", "EV/FCF", "EV/EBITDA",
        "ROIC", "ROE", "ROA", "PEG (Trailing)", "PEG (Forward)", "EPS",
        "Market Cap", "Revenue", "Gross Profit", "Debt / Equity", "Enterprise Value",
        "Dividend Yield", "Payout Ratio", "MOAT"
    ],
    "Value": [
        ticker, "2025-03-31", industry, sector, description,
        f"{pe:.2f}" if pe else "NONE",
        f"{pb:.2f}" if pb else "NONE",
        f"${fcf / 1e6:.2f} Million" if fcf else "NONE",
        f"{ev_fcf:.2f}" if ev_fcf else "NONE",
        f"{ev_ebitda:.2f}" if ev_ebitda else "NONE",
        f"{roic:.2f}%" if roic else "NONE",
        f"{roe:.2f}%" if roe else "NONE",
        f"{roa:.2f}%" if roa else "NONE",
        f"{peg_trailing:.2f}" if peg_trailing else "NONE",
        f"{peg_forward:.2f}" if peg_forward else "NONE",
        f"{eps:.2f}" if eps else "NONE",
        f"${market_cap / 1e9:.2f} Billion" if market_cap else "NONE",
        f"${revenue / 1e6:.2f} Million" if revenue else "NONE",
        f"${gross_profit / 1e6:.2f} Million" if gross_profit else "NONE",
        f"{de_ratio:.2f}" if de_ratio else "NONE",
        f"${ev / 1e9:.2f} Billion" if ev else "NONE",
        "NONE",  # Dividend Yield
        "NONE",  # Payout Ratio
        "See below"
    ],
    "Period": [
        "-", "Q1 2025", "Q1 2025", "Q1 2025", "-", 
        "TTM", "Q1 2025", "Q1 2025", "Q1 2025", "TTM",
        "TTM", "TTM", "TTM", "TTM", "TTM", "TTM",
        "Q1 2025", "Q1 2025", "Q1 2025", "Q1 2025", "Q1 2025",
        "Q1 2025", "Q1 2025", "-"
    ]
}

df = pd.DataFrame(data)

# Display table
st.dataframe(df, use_container_width=True)

# Moat analysis
st.markdown("### 🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
st.markdown("""
Perimeter Solutions appears to possess elements of a **narrow economic moat** due to:

- **Specialized Niche**: One of the few global providers of wildfire retardants and foams under long-term government contracts.
- **High Switching Costs**: Municipalities and agencies face safety/logistical hurdles in changing vendors.
- **Regulatory Barriers**: Compliance and certifications slow new entrants.
- **R&D and IP**: Differentiation in phosphorus additive chemistry.

**Weaknesses**:
- Low ROIC and erratic FCF signal efficiency concerns.
- Seasonality of revenue makes cash flow less predictable.

**Conclusion**: Narrow moat, built on regulatory and technical entrenchment, though financials remain uneven.
""")
