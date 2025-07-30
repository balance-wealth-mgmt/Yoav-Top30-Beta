import streamlit as st
import requests
import pandas as pd
import math

# --- Title ---
st.set_page_config(page_title="PRM.US Dashboard", layout="centered")
st.title("Perimeter Solutions (PRM.US) Financial Dashboard")

# --- API Setup ---
api_key = st.secrets["EODHD_API_KEY"]
base_url = "https://eodhd.com/api/fundamentals/PRM.US"

# --- Helper Functions ---
@st.cache_data
def get_fundamentals():
    url = f"{base_url}?api_token={api_key}&fmt=json"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}

def safe_get(dct, *keys):
    for key in keys:
        dct = dct.get(key, {})
    return dct or None

def calc_roic(net_income, total_debt, total_equity):
    invested_capital = total_debt + total_equity if (total_debt and total_equity) else None
    return (net_income / invested_capital) if invested_capital else None

def calc_debt_equity(total_debt, total_equity):
    return (total_debt / total_equity) if (total_debt and total_equity) else None

def calc_peg(pe_ratio, growth_rate):
    return (pe_ratio / growth_rate) if (pe_ratio and growth_rate) else None

# --- Data Fetch ---
data = get_fundamentals()

# --- Extracted Fields ---
general = data.get("General", {})
highlights = data.get("Highlights", {})
valuation = data.get("Valuation", {})
sector = general.get("Sector", "NONE")
industry = general.get("Industry", "NONE")
description = general.get("Description", "NONE")

# Latest quarterly free cash flow
q_cashflow = safe_get(data, "Financials", "Cash_Flow", "quarterly", "2025-03-31")
fcf = q_cashflow.get("freeCashFlow") if q_cashflow else None

# Balance sheet values for calculations
q_balance = safe_get(data, "Financials", "Balance_Sheet", "quarterly", "2025-03-31")
total_debt = q_balance.get("totalDebt") if q_balance else None
total_equity = q_balance.get("totalEquity") if q_balance else None

# Income statement for ROIC
q_income = safe_get(data, "Financials", "Income_Statement", "quarterly", "2025-03-31")
net_income = q_income.get("netIncome") if q_income else None

# --- Calculations ---
pe_ratio = highlights.get("PERatioTTM")
pb_ratio = valuation.get("PriceBookMRQ")
ev = valuation.get("EnterpriseValue")
ev_ebitda = valuation.get("EnterpriseValueEBITDA")
eps = highlights.get("EarningsShare")
roe = highlights.get("ReturnOnEquityTTM")
roa = highlights.get("ReturnOnAssetsTTM")
div_yield = highlights.get("DividendYield")
payout_ratio = highlights.get("PayoutRatio")
market_cap = highlights.get("MarketCapitalization")
revenue = highlights.get("RevenueTTM")
gross_profit = highlights.get("GrossProfitTTM")
peg_ratio = calc_peg(pe_ratio, highlights.get("EarningsGrowth", 0.01))  # fallback to avoid div by 0
roic = calc_roic(net_income, total_debt, total_equity)
de_ratio = calc_debt_equity(total_debt, total_equity)

# --- Display Table ---
st.subheader("📊 Key Metrics")

table_data = {
    "Ticker": ["PRM.US"],
    "Date": ["2025-03-31"],
    "Sector": [sector],
    "Industry": [industry],
    "P/E": [pe_ratio],
    "P/B": [pb_ratio],
    "EPS": [eps],
    "Market Cap": [market_cap],
    "Revenue": [revenue],
    "Gross Profit": [gross_profit],
    "Free Cash Flow": [fcf],
    "EV": [ev],
    "EV/EBITDA": [ev_ebitda],
    "ROE (TTM)": [roe],
    "ROA (TTM)": [roa],
    "ROIC": [roic],
    "Debt / Equity": [de_ratio],
    "PEG": [peg_ratio],
    "Dividend Yield": [div_yield],
    "Payout Ratio": [payout_ratio],
}

df = pd.DataFrame(table_data).T
df.columns = ["Value"]
st.dataframe(df)

# --- Description ---
st.subheader("🏢 Company Description")
st.markdown(description)

# --- Moat Analysis ---
st.subheader("🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
st.markdown("""
Perimeter Solutions appears to possess elements of a **narrow economic moat** due to:

- **Specialized Niche**: PRM is one of very few global providers of wildfire retardants and foams under long-term contracts with agencies like the U.S. Forest Service.
- **High Switching Costs**: Regulatory and logistical barriers prevent easy supplier substitution.
- **Regulatory Barriers**: Certification and approval processes discourage new market entrants.
- **R&D and IP**: Specialized phosphorus pentasulfide-based additives help differentiate PRM technically.

**Weaknesses:**
- Low ROIC and limited FCF suggest efficiency concerns.
- Seasonality from wildfire activity impacts cash flows.

**Conclusion**: PRM exhibits a **narrow moat**, supported by regulatory entrenchment and mission-critical products, though financials remain a concern.
""")

# --- Footer ---
st.caption("Data provided by EODHD.com")
