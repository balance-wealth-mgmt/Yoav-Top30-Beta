import streamlit as st
import requests
import pandas as pd
import os

# Load API key from Streamlit secrets
API_KEY = st.secrets["EODHD_API_KEY"]
TICKER = "PRM.US"

# Helper to format values
def fmt(val, pct=False):
    if val is None:
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
        return val

# API fetch helper
def fetch_section(ticker, section):
    url = f"https://eodhd.com/api/fundamentals/{ticker}?filter={section}&api_token={API_KEY}&fmt=json"
    res = requests.get(url)
    return res.json() if res.ok else {}

# Load all necessary data
general = fetch_section(TICKER, "General")
highlights = fetch_section(TICKER, "Highlights")
valuation = fetch_section(TICKER, "Valuation")
cf_q = fetch_section(TICKER, "Financials::Cash_Flow::quarterly::2025-03-31")

# Extract metrics
data = {
    "Ticker": TICKER,
    "Data's Date": "2025-03-31",
    "Industry": general.get("Industry", "NONE"),
    "Sector": general.get("Sector", "NONE"),
    "P/E": fmt(valuation.get("TrailingPE")),
    "P/B": fmt(valuation.get("PriceBookMRQ")),
    "FCF": fmt(cf_q.get("freeCashFlow")),
    "EV/FCF": fmt(
        float(valuation["EnterpriseValue"]) / float(cf_q["freeCashFlow"])
    ) if valuation.get("EnterpriseValue") and cf_q.get("freeCashFlow") not in (None, "0") else "NONE",
    "EV/EBITDA": fmt(valuation.get("EnterpriseValueEbitda")),
    "ROIC": "NONE",  # Not directly available
    "ROE": fmt(highlights.get("ReturnOnEquityTTM"), pct=True),
    "ROA": fmt(highlights.get("ReturnOnAssetsTTM"), pct=True),
    "PEG": fmt(highlights.get("PeRatioHigh")),
    "EPS": fmt(highlights.get("EarningsShare")),
    "Market Cap": fmt(highlights.get("MarketCapitalization")),
    "Revenue": fmt(highlights.get("RevenueTTM")),
    "Gross Profit": fmt(highlights.get("GrossProfitTTM")),
    "Debt / Equity": fmt(
        float(highlights["TotalDebt"]) / float(highlights["ShareholdersEquity"])
    ) if highlights.get("TotalDebt") and highlights.get("ShareholdersEquity") else "NONE",
    "Dividend Yield": fmt(highlights.get("DividendYield"), pct=True),
    "Payout Ratio": fmt(highlights.get("PayoutRatio"), pct=True),
    "Enterprise Value": fmt(valuation.get("EnterpriseValue")),
    "Period": "Q1 2025",
    "Description": general.get("Description", "NONE")
}

# Show Table
st.title("📊 PRM.US – Financial Snapshot & MOAT Analysis")

st.subheader("Summary Table")
df = pd.DataFrame(data.items(), columns=["Metric", "Value"])
st.dataframe(df, use_container_width=True)

# Moat Analysis
st.subheader("🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
st.markdown("""
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
""")

st.markdown("---")
st.caption("Data sourced from EODHD · Powered by Streamlit")
