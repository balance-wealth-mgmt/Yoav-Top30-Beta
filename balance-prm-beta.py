import streamlit as st
import requests
import pandas as pd

# Load API key securely
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

# Fetch sections
general = fetch_section(TICKER, "General")
highlights = fetch_section(TICKER, "Highlights")
valuation = fetch_section(TICKER, "Valuation")
cf_q = fetch_section(TICKER, "Financials::Cash_Flow::quarterly::2025-03-31")

# Safe value extractor
def safe_get(d, key):
    return d.get(key) if d and isinstance(d, dict) else None

# Financial Calculations
pe_ratio = safe_get(valuation, "TrailingPE")
eps_growth = safe_get(highlights, "EpsGrowth")
peg_ratio = float(pe_ratio) / float(eps_growth) if pe_ratio and eps_growth else None

debt = safe_get(highlights, "TotalDebt")
equity = safe_get(highlights, "ShareholdersEquity")
debt_equity = float(debt) / float(equity) if debt and equity else None

net_income = safe_get(highlights, "NetIncome")
tax_rate = 0.21
nopat = float(net_income) * (1 - tax_rate) if net_income else None
capital = float(debt) + float(equity) if debt and equity else None
roic = float(nopat) / float(capital) if nopat and capital else None

ev = safe_get(valuation, "EnterpriseValue")
fcf = safe_get(cf_q, "freeCashFlow")
ev_fcf = float(ev) / float(fcf) if ev and fcf and float(fcf) != 0 else None

# Build dataset
data = {
    "Ticker": TICKER,
    "Data's Date": "2025-03-31",
    "Industry": safe_get(general, "Industry"),
    "Sector": safe_get(general, "Sector"),
    "P/E": fmt(pe_ratio),
    "P/B": fmt(safe_get(valuation, "PriceBookMRQ")),
    "FCF": fmt(fcf),
    "E
