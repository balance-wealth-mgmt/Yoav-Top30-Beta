from pathlib import Path

# Rewriting the full corrected script again after kernel reset
final_script = """
import streamlit as st
import requests
import pandas as pd

# Load API key from secrets
API_KEY = st.secrets["EODHD_API_KEY"]
TICKER = "PRM.US"

def fmt(val, pct=False):
    if val is None or val == 0:
        return "NONE"
    try:
        val = float(val)
        if pct:
            return f"{val:.2f}%"
        elif abs(val) >= 1e9:
            return f"{val / 1e9:.2f}B"
        elif abs(val) >= 1e6:
            return f"{val / 1e6:.2f}M"
        elif abs(val) >= 1e3:
            return f"{val / 1e3:.2f}K"
        else:
            return f"{val:.2f}"
    except:
        return "NONE"

def fetch_section(ticker, section):
    url = f"https://eodhd.com/api/fundamentals/{ticker}?filter={section}&api_token={API_KEY}&fmt=json"
    res = requests.get(url)
    return res.json() if res.ok else {}

# Fetch all sections
general = fetch_section(TICKER, "General")
highlights = fetch_section(TICKER, "Highlights")
valuation = fetch_section(TICKER, "Valuation")
cf_q = fetch_section(TICKER, "Financials::Cash_Flow::quarterly::2025-03-31")

# Extract values with fallback
def safe_get(d, key):
    return d.get(key) if d and isinstance(d, dict) else None

# PEG fallback calc (PE / growth %), if PE and EPS growth available
pe_ratio = safe_get(valuation, "TrailingPE")
eps_growth = safe_get(highlights, "EpsGrowth")
peg_ratio = float(pe_ratio) / float(eps_growth) if pe_ratio and eps_growth else None

# Debt/Equity calc
debt = safe_get(highlights, "TotalDebt")
equity = safe_get(highlights, "ShareholdersEquity")
debt_equity = float(debt) / float(equity) if debt and equity else None

# ROIC approx = NOPAT / (Total Debt + Equity)
net_income = safe_get(highlights, "NetIncome")
tax_rate = 0.21
nopat = float(net_income) * (1 - tax_rate) if net_income else None
capital = float(debt) + float(equity) if debt and equity else None
roic = float(nopat) / float(capital) if nopat and capital else None

# EV/FCF
ev = safe_get(valuation, "EnterpriseValue")
fcf = safe_get(cf_q, "freeCashFlow")
ev_fcf = float(ev) / float(fcf) if ev and fcf and float(fcf) != 0 else None

data = {
    "Ticker": TICKER,
    "Data's Date": "2025-03-31",
    "Industry": safe_get(general, "Industry"),
    "Sector": safe_get(general, "Sector"),
    "P/E": fmt(pe_ratio),
    "P/B": fmt(safe_get(valuation, "PriceBookMRQ")),
    "FCF": fmt(fcf),
    "EV/FCF": fmt(ev_fcf),
    "EV/EBITDA": fmt(safe_get(valuation, "EnterpriseValueEbitda")),
    "ROIC": fmt(roic, pct=True),
    "ROE": fmt(safe_get(highlights, "ReturnOnEquityTTM"), pct=True),
    "ROA": fmt(safe_get(highlights, "ReturnOnAssetsTTM"), pct=True),
    "PEG": fmt(peg_ratio),
    "EPS": fmt(safe_get(highlights, "EarningsShare")),
    "Market Cap": fmt(safe_get(highlights, "MarketCapitalization")),
    "Revenue": fmt(safe_get(highlights, "RevenueTTM")),
    "Gross Profit": fmt(safe_get(highlights, "GrossProfitTTM")),
    "Debt / Equity": fmt(debt_equity),
    "Dividend Yield": fmt(safe_get(highlights, "DividendYield"), pct=True),
    "Payout Ratio": fmt(safe_get(highlights, "PayoutRatio"), pct=True),
    "Enterprise Value": fmt(ev),
    "Period": "Q1 2025",
    "Description": safe_get(general, "Description")
}

st.title("📊 PRM.US – Financial Snapshot & MOAT Analysis")
st.subheader("Summary Table")
df = pd.DataFrame(data.items(), columns=["Metric", "Value"])
st.dataframe(df, use_container_width=True)

st.subheader("🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
st.markdown(\"""
Perimeter Solutions appears to possess elements of a **narrow economic moat** due to:

- **Specialized Niche**: The company is one of very few global providers of wildfire retardants and foams, operating under long-term contracts with federal agencies like the U.S. Forest Service.
- **High Switching Costs**: Governments and municipalities are unlikely to switch suppliers easily due to safety, approval, and logistic constraints — giving PRM a defensible position.
- **Regulatory Barriers**: Fire retardant products often require certifications and lengthy compliance processes, reducing new entrant threats.
- **R&D and IP**: The specialty chemicals segment relies on unique formulations and expertise in phosphorus pentasulfide-based additives, which provides technical differentiation.

### Weaknesses:
- **Low ROIC and weak FCF** indicate operational inefficiencies.
- **Seasonal revenue** tied to wildfire activity makes cash flows less predictable.

### 🔍 Conclusion:
PRM exhibits a **narrow moat**, driven primarily by regulatory entrenchment and mission-critical products, though financials (e.g., FCF and ROIC) do not yet reinforce long-term economic power.
\""")
st.markdown("---")
st.caption("Data sourced from EODHD · Powered by Streamlit")
"""

# Save the updated script
script_path = "/mnt/data/app_corrected_full.py"
Path(script_path).write_text(final_script)
script_path
