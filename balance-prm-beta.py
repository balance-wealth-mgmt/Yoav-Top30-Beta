import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PRM.US Financial Dashboard", layout="wide")

# Load secrets
api_key = st.secrets["eodhd"]["api_key"]
ticker = "PRM.US"

@st.cache_data(ttl=3600)
def get_fundamentals(ticker):
    base_url = "https://eodhd.com/api/fundamentals"
    url = f"{base_url}/{ticker}?api_token={api_key}&fmt=json"
    return requests.get(url).json()

data = get_fundamentals(ticker)

# Extract and calculate metrics
def safe_get(d, keys, default="NONE"):
    for key in keys:
        if d and key in d:
            d = d[key]
        else:
            return default
    return d

valuation = data.get("Valuation", {})
highlights = data.get("Highlights", {})
general = data.get("General", {})
financials = data.get("Financials", {}).get("Cash_Flow", {}).get("quarterly", {}).get("2025-03-31", {})
balance = data.get("Financials", {}).get("Balance_Sheet", {}).get("quarterly", {}).get("2025-03-31", {})

pe = safe_get(valuation, ["TrailingPE"])
pb = safe_get(valuation, ["PriceBookMRQ"])
eps = safe_get(highlights, ["EarningsShare"])
fcf = safe_get(financials, ["freeCashFlow"])
ev = safe_get(valuation, ["EnterpriseValue"])
ev_ebitda = safe_get(valuation, ["EnterpriseValueEbitda"])
roe = safe_get(highlights, ["ReturnOnEquityTTM"])
roa = safe_get(highlights, ["ReturnOnAssetsTTM"])
revenue = safe_get(highlights, ["RevenueTTM"])
gross_profit = safe_get(highlights, ["GrossProfitTTM"])
market_cap = safe_get(highlights, ["MarketCapitalization"])
div_yield = safe_get(highlights, ["DividendYield"])
payout = safe_get(highlights, ["PayoutRatio"])
industry = safe_get(general, ["Industry"])
sector = safe_get(general, ["Sector"])
description = safe_get(general, ["Description"])
total_debt = safe_get(balance, ["shortLongTermDebtTotal", "shortTermDebt"]) or 0
equity = safe_get(balance, ["totalStockholderEquity"]) or 0

# Calculated fields
try:
    peg = round(float(pe) / (float(highlights.get("EarningsGrowth", 0)) or 1), 2)
except:
    peg = "NONE"

try:
    roic = round(float(highlights.get("OperatingIncome", 0)) / (float(highlights.get("InvestedCapital", 0)) or 1), 2)
except:
    roic = "NONE"

try:
    debt_equity = round(float(total_debt) / (float(equity) or 1), 2)
except:
    debt_equity = "NONE"

try:
    ev_fcf = round(float(ev) / (float(fcf) or 1), 2)
except:
    ev_fcf = "NONE"

metrics = {
    "Ticker": ticker,
    "Data's Date": "2025-03-31",
    "Industry": industry,
    "Sector": sector,
    "P/E": pe,
    "P/B": pb,
    "FCF": fcf,
    "EV/FCF": ev_fcf,
    "EV/EBITDA": ev_ebitda,
    "ROIC": roic,
    "ROE": roe,
    "ROA": roa,
    "PEG": peg,
    "EPS": eps,
    "Market Cap": market_cap,
    "Enterprise Value": ev,
    "Revenue": revenue,
    "Gross Profit": gross_profit,
    "Debt / Equity": debt_equity,
    "Dividend Yield": div_yield,
    "Payout Ratio": payout,
    "TTM/Q1": {
        "ROA": "TTM", "ROE": "TTM", "EPS": "TTM", "Revenue": "TTM", "Gross Profit": "TTM"
    }
}

df = pd.DataFrame.from_dict(metrics, orient='index', columns=["Value"])
st.title("📊 Perimeter Solutions (PRM.US) Financial Overview")
st.dataframe(df)

st.subheader("🧾 Description")
st.write(description)

st.subheader("🛡️ MOAT Analysis")
st.markdown(\"""
**Perimeter Solutions** appears to possess elements of a **narrow economic moat** due to:

- **Specialized Niche**: One of few global providers of wildfire retardants and foams, working with agencies like the U.S. Forest Service.
- **High Switching Costs**: Governments and municipalities rarely switch suppliers due to safety and logistic dependencies.
- **Regulatory Barriers**: Products require certifications and compliance, limiting new entrants.
- **R&D and IP**: Unique formulations for phosphorus pentasulfide-based additives offer technical advantages.

**Weaknesses**:
- Low ROIC and weak FCF highlight operational inefficiencies.
- Highly seasonal revenue tied to wildfire activity introduces cash flow unpredictability.

**Conclusion**: PRM exhibits a **narrow moat** due to regulatory entrenchment and mission-critical offerings. Financial performance, however, does not yet confirm strong long-term advantages.
\""")
