import streamlit as st
import requests

# Load API token securely
try:
    eodhd_token = st.secrets["eodhd"]["api_key"]
except Exception:
    st.error("Please set your EODHD API token in Streamlit secrets as `eodhd.api_key`.")
    st.stop()

ticker = "PRM.US"
base_url = "https://eodhd.com/api"
headers = {"Accept": "application/json"}

# Utility functions
def get_json(url, params={}):
    params["api_token"] = eodhd_token
    params["fmt"] = "json"
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def fetch_fundamentals():
    return get_json(f"{base_url}/fundamentals/{ticker}")

def fetch_financials():
    return get_json(f"{base_url}/fundamentals/{ticker}", {"filter": "Financials::Cash_Flow::quarterly"})

def fetch_ratios():
    return get_json(f"{base_url}/fundamentals/{ticker}", {"filter": "Financials::Ratios::quarterly"})

def fetch_valuation():
    return get_json(f"{base_url}/fundamentals/{ticker}", {"filter": "Valuation"})

def fetch_technicals():
    return get_json(f"{base_url}/fundamentals/{ticker}", {"filter": "Technicals"})

def fetch_highlights():
    return get_json(f"{base_url}/fundamentals/{ticker}", {"filter": "Highlights"})

# Build Streamlit UI
st.set_page_config(page_title="PRM.US Fundamental Analysis", layout="wide")
st.title("📊 PRM.US - Fundamental Analysis & MOAT Assessment")

# Pull data
fundamentals = fetch_fundamentals()
highlights = fetch_highlights()
valuation = fetch_valuation()
technicals = fetch_technicals()
ratios = fetch_ratios()
cash_flows = fetch_financials()

desc = fundamentals.get("General", {}).get("Description", "—")
sector = fundamentals.get("General", {}).get("Sector", "—")
industry = fundamentals.get("General", {}).get("Industry", "—")

# Extract Metrics
pe = highlights.get("PERatio")
pb = highlights.get("PriceBookMRQ")
eps = highlights.get("EPS")
div_yield = highlights.get("DividendYield")
payout = highlights.get("PayoutRatio")
market_cap = valuation.get("Market_Capitalization")
ev = valuation.get("Enterprise_Value")
ev_ebitda = valuation.get("EVToEBITDA")
peg_trailing = valuation.get("PEGRatio")
peg_forward = valuation.get("ForwardPEGRatio")
roe = ratios.get("2025-03-31", {}).get("ReturnOnEquity")
roa = ratios.get("2025-03-31", {}).get("ReturnOnAssets")
roic = ratios.get("2025-03-31", {}).get("ReturnOnInvestedCapital")
debt_equity = ratios.get("2025-03-31", {}).get("DebtEquityRatio")
revenue = fundamentals.get("Financials", {}).get("Income_Statement", {}).get("quarterly", {}).get("2025-03-31", {}).get("totalRevenue")
gross_profit = fundamentals.get("Financials", {}).get("Income_Statement", {}).get("quarterly", {}).get("2025-03-31", {}).get("grossProfit")
fcf = fundamentals.get("Financials", {}).get("Cash_Flow", {}).get("quarterly", {}).get("2025-03-31", {}).get("freeCashFlow")

# Calculate EV/FCF
ev_fcf = ev / fcf if fcf and ev else None

# Build table
st.subheader("📋 Key Metrics (Q1 2025 / TTM)")
table_data = []

def add_metric(name, value, period):
    table_data.append((name, value if value is not None else "—", period))

add_metric("Ticker", ticker, "—")
add_metric("Data's Date", "2025-03-31", "Q1 2025")
add_metric("Industry", industry, "Q1 2025")
add_metric("Sector", sector, "Q1 2025")
add_metric("Description", desc, "—")
add_metric("P/E", f"{pe:.2f}" if pe else None, "TTM")
add_metric("P/B", f"{pb:.2f}" if pb else None, "Q1 2025")
add_metric("FCF", f"${fcf/1e6:.2f} Million" if fcf is not None else None, "Q1 2025")
add_metric("EV/FCF", f"{ev_fcf:.2f}" if ev_fcf else None, "Q1 2025")
add_metric("EV/EBITDA", f"{ev_ebitda:.2f}" if ev_ebitda else None, "TTM")
add_metric("ROIC", f"{roic*100:.2f}%" if roic else None, "TTM")
add_metric("ROE", f"{roe*100:.2f}%" if roe else None, "TTM")
add_metric("ROA", f"{roa*100:.2f}%" if roa else None, "TTM")
add_metric("PEG (Trailing)", f"{peg_trailing:.2f}" if peg_trailing else None, "TTM")
add_metric("PEG (Forward)", f"{peg_forward:.2f}" if peg_forward else None, "TTM")
add_metric("EPS", f"{eps:.2f}" if eps else None, "TTM")
add_metric("Market Cap", f"${market_cap/1e9:.2f} Billion" if market_cap else None, "Q1 2025")
add_metric("Revenue", f"${revenue/1e6:.2f} Million" if revenue else None, "Q1 2025")
add_metric("Gross Profit", f"${gross_profit/1e6:.2f} Million" if gross_profit else None, "Q1 2025")
add_metric("Debt / Equity", f"{debt_equity:.2f}" if debt_equity else None, "Q1 2025")
add_metric("Enterprise Value", f"${ev/1e9:.2f} Billion" if ev else None, "Q1 2025")
add_metric("Dividend Yield", f"{div_yield*100:.2f}%" if div_yield else "NONE", "Q1 2025")
add_metric("Payout Ratio", f"{payout*100:.2f}%" if payout else "NONE", "Q1 2025")
add_metric("MOAT", "See Below", "—")

st.dataframe(table_data, use_container_width=True, hide_index=True)

# Add MOAT section
st.subheader("🛡 MOAT Analysis")
st.markdown("""
**PRM.US** shows characteristics of a narrow economic moat:
- Specialized products in firefighting & chemical additives
- Moderate ROIC (4.19%) and strong Gross Margin
- High Debt/Equity (2.57), but growing FCF
- PEG Ratio Forward (4.14) suggests expected slower growth

Overall: **Emerging MOAT** — worth watching closely as fundamentals improve.
""")
