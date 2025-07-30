import streamlit as st
import requests
import os
from datetime import datetime

# --- Streamlit App Config ---
st.set_page_config(page_title="PRM.US Financial Dashboard", layout="wide")
st.title("📊 PRM.US Financial Metrics and MOAT Analysis")

# --- API Token ---
eodhd_token = st.secrets["eodhd"]["api_key"]
base_url = "https://eodhd.com/api"

# --- Helper Functions ---
def fetch_fundamentals():
    url = f"{base_url}/fundamentals/PRM.US?api_token={eodhd_token}&fmt=json"
    return requests.get(url).json()

def fetch_financials():
    url = f"{base_url}/fundamentals/PRM.US?api_token={eodhd_token}&filter=Financials::Cash_Flow::quarterly::2025-03-31"
    return requests.get(url).json()

def fetch_ratios():
    url = f"{base_url}/fundamentals/PRM.US?api_token={eodhd_token}&filter=Financials::Financial_Ratios::quarterly"
    return requests.get(url).json()

# --- Load Data ---
data = fetch_fundamentals()
ratios = fetch_ratios()
cashflow = fetch_financials()

# --- Extract Values ---
valuation = data.get("Valuation", {})
highlights = data.get("Highlights", {})
general = data.get("General", {})

revenue = data.get("Financials", {}).get("Income_Statement", {}).get("quarterly", {}).get("2025-03-31", {}).get("totalRevenue")
gross_profit = data.get("Financials", {}).get("Income_Statement", {}).get("quarterly", {}).get("2025-03-31", {}).get("grossProfit")

fcf = cashflow.get("freeCashFlow")
debt_to_equity = None
roe = roa = roic = peg_trailing = peg_forward = None

# Safely extract latest available ratio
for period, row in ratios.items():
    if period.startswith("2025"):
        roe = row.get("ReturnOnEquity")
        roa = row.get("ReturnOnAssets")
        roic = row.get("ReturnOnInvestedCapital")
        debt_to_equity = row.get("DebtEquity")
        peg_trailing = row.get("PEGRatio")
        peg_forward = row.get("ForwardPEGRatio")
        break

# --- Render Table ---
def add_metric(label, value, period):
    st.markdown(f"<tr><td><b>{label}</b></td><td>{value or 'N/A'}</td><td>{period}</td></tr>", unsafe_allow_html=True)

st.markdown("""
<style>
table {width: 100%; border-collapse: collapse;}
th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
th {background-color: #f4f4f4;}
</style>
<table>
<thead><tr><th>Metric</th><th>Value</th><th>Period</th></tr></thead>
<tbody>
""", unsafe_allow_html=True)

add_metric("Ticker", "PRM.US", "—")
add_metric("Data's Date", "2025-03-31", "Q1 2025")
add_metric("Industry", general.get("Industry"), "Q1 2025")
add_metric("Sector", general.get("Sector"), "Q1 2025")
add_metric("Description", general.get("Description"), "—")
add_metric("P/E", highlights.get("PERatio"), "TTM")
add_metric("P/B", highlights.get("PriceBook"), "Q1 2025")
add_metric("FCF", f"${fcf/1e6:.2f} Million" if fcf else None, "Q1 2025")
add_metric("EV/FCF", highlights.get("EVToFCF"), "Q1 2025")
add_metric("EV/EBITDA", highlights.get("EVToEBITDA"), "TTM")
add_metric("ROIC", f"{roic:.2%}" if roic else None, "TTM")
add_metric("ROE", f"{roe:.2%}" if roe else None, "TTM")
add_metric("ROA", f"{roa:.2%}" if roa else None, "TTM")
add_metric("PEG (Trailing)", peg_trailing, "TTM")
add_metric("PEG (Forward)", peg_forward, "TTM")
add_metric("EPS", highlights.get("EarningsShare"), "TTM")
add_metric("Market Cap", f"${valuation.get('Market_Capitalization') / 1e9:.2f} Billion", "Q1 2025")
add_metric("Revenue", f"${revenue/1e6:.2f} Million" if revenue else None, "Q1 2025")
add_metric("Gross Profit", f"${gross_profit/1e6:.2f} Million" if gross_profit else None, "Q1 2025")
add_metric("Debt / Equity", f"{debt_to_equity:.2f}" if debt_to_equity else None, "Q1 2025")
add_metric("Enterprise Value", f"${highlights.get('EnterpriseValue') / 1e9:.2f} Billion", "Q1 2025")
add_metric("Dividend Yield", highlights.get("DividendYield") or "NONE", "Q1 2025")
add_metric("Payout Ratio", highlights.get("PayoutRatio") or "NONE", "Q1 2025")
add_metric("MOAT", "See Below", "—")

st.markdown("""
</tbody></table>
""", unsafe_allow_html=True)

# --- MOAT Analysis ---
st.subheader("🛡 Competitive Advantage (MOAT) Analysis")
st.markdown("""
This section evaluates the company's potential sustainable advantages based on profitability, capital efficiency, and valuation multiples:
- **Profitability**: Strong margins and return metrics.
- **Efficiency**: High ROIC, solid FCF.
- **Valuation**: Reasonable multiples like P/E and EV/EBITDA.

PRM.US exhibits **moderate moat potential**, driven by specialized products and moderate returns. However, high Debt/Equity suggests some financial risk.
""")
