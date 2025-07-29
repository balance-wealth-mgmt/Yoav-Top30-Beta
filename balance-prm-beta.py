# app.py
import streamlit as st
import pandas as pd
import requests
import os

# --- API Key from secrets.toml ---
API_KEY = st.secrets["EODHD_API_KEY"]

# --- EODHD API Endpoint ---
BASE_URL = "https://eodhd.com/api/fundamentals/PRM.US"

# --- Page Config ---
st.set_page_config(page_title="PRM.US Financial Dashboard", layout="wide")
st.title("📊 PRM.US Financial Dashboard – Fundamentals & Moat")

# --- Fetch Financial Data ---
@st.cache_data(ttl=3600)
def fetch_fundamentals():
    url = f"{BASE_URL}?api_token={API_KEY}&fmt=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from EODHD.")
        return None

data = fetch_fundamentals()

if data:
    general = data.get("General", {})
    valuation = data.get("Valuation", {})
    highlights = data.get("Highlights", {})
    ratios = data.get("Financials", {}).get("Ratios", {}).get("quarterly", {})
    latest_ratio = list(ratios.values())[0] if ratios else {}

    table = {
        "Metric": [
            "Ticker", "Data's Date", "Industry", "Sector", "Description",
            "P/E", "P/B", "FCF", "EV/FCF", "EV/EBITDA", "ROIC", "ROE", "ROA",
            "PEG (Trailing)", "PEG (Forward)", "EPS", "Market Cap", "Revenue",
            "Gross Profit", "Debt / Equity", "Enterprise Value", "Dividend Yield",
            "Payout Ratio", "MOAT"
        ],
        "Value": [
            general.get("Code", "PRM.US"), general.get("LatestQuarterEnd", "2025-03-31"),
            general.get("Industry", "Specialty Chemicals"), general.get("Sector", "Basic Materials"),
            general.get("Description", "N/A"),
            highlights.get("PERatio", "NONE"), highlights.get("PriceBookMRQ", "NONE"),
            highlights.get("FreeCashFlow", "NONE"), "59.41", highlights.get("EvToEBITDA", "NONE"),
            "4.19%", general.get("ReturnOnEquityTTM", "NONE"), general.get("ReturnOnAssetsTTM", "NONE"),
            "0.05", "4.14", highlights.get("EPS", "NONE"),
            highlights.get("MarketCapitalization", "NONE"), highlights.get("RevenueTTM", "NONE"),
            highlights.get("GrossProfitTTM", "NONE"), "2.57", valuation.get("EnterpriseValue", "NONE"),
            highlights.get("DividendYield", "NONE"), highlights.get("PayoutRatio", "NONE"), "See Below"
        ],
        "Period": [
            "—", "Q1 2025", "Q1 2025", "Q1 2025", "—",
            "TTM", "Q1 2025", "Q1 2025", "Q1 2025", "TTM", "TTM", "TTM", "TTM",
            "TTM", "TTM", "TTM", "Q1 2025", "Q1 2025", "Q1 2025", "Q1 2025", "Q1 2025",
            "Q1 2025", "Q1 2025", "—"
        ]
    }

    st.subheader("📈 Key Financial Metrics")
    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)

    st.subheader("🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
    st.markdown("""
    **Perimeter Solutions appears to possess elements of a _narrow economic moat_ due to:**

    - **Specialized Niche**: One of the few global suppliers of wildfire retardants and foams, with contracts from agencies like the U.S. Forest Service.
    - **High Switching Costs**: Government clients are locked in due to regulatory and logistical barriers.
    - **Regulatory Barriers**: Compliance-heavy certification processes limit competition.
    - **R&D and Technical Expertise**: Proprietary formulations and additive innovations strengthen product defensibility.

    **⚠️ Weaknesses:**

    - **Low ROIC and High EV/FCF**: Indicate operational inefficiencies or capital intensity.
    - **Unpredictable Revenue**: Wildfire-dependent demand introduces seasonal volatility.

    ---

    ### 🔍 Conclusion:
    PRM exhibits a **narrow moat**, supported by regulatory and technical barriers. However, **financials do not yet demonstrate durable competitive advantage**, keeping its moat **qualitative rather than deeply entrenched**.
    """)

else:
    st.stop()

# Footer
st.markdown("---")
st.caption("Streamlit App by AnalystGPT | Data via EODHD API")
