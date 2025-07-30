import streamlit as st
import requests
import os

# Load EODHD API key securely
api_key = st.secrets["eodhd"]["api_key"]
ticker = "PRM.US"

@st.cache_data(show_spinner=True)
def fetch_fundamentals(symbol: str, section: str):
    url = f"https://eodhd.com/api/fundamentals/{symbol}?filter={section}&api_token={api_key}&fmt=json"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {}

@st.cache_data(show_spinner=True)
def fetch_fundamental_point(symbol: str, section: str, point: str):
    url = f"https://eodhd.com/api/fundamentals/{symbol}?filter={section}::{point}&api_token={api_key}&fmt=json"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {}

st.title(f"🧾 Financial Dashboard — {ticker}")
st.write("All data sourced via EODHD API.")

# --- Fetch Data ---
general = fetch_fundamentals(ticker, "General")
highlights = fetch_fundamentals(ticker, "Highlights")
valuation = fetch_fundamentals(ticker, "Valuation")
cash_flow_q = fetch_fundamentals(ticker, "Financials::Cash_Flow::quarterly::2025-03-31")
bs_q = fetch_fundamentals(ticker, "Financials::Balance_Sheet::quarterly::2025-03-31")
income_q = fetch_fundamentals(ticker, "Financials::Income_Statement::quarterly::2025-03-31")

# --- Extract Metrics ---
metrics = []

def add_metric(label, value, period):
    metrics.append((label, value if value is not None else "N/A", period))

add_metric("Ticker", ticker, "—")
add_metric("Data's Date", "2025-03-31", "Q1 2025")
add_metric("Industry", general.get("Industry"), "Q1 2025")
add_metric("Sector", general.get("Sector"), "Q1 2025")
add_metric("Description", general.get("Description"), "—")
add_metric("P/E", valuation.get("TrailingPE"), "TTM")
add_metric("P/B", valuation.get("PriceBookMRQ"), "Q1 2025")

fcf = cash_flow_q.get("freeCashFlow")
add_metric("FCF", f"${fcf/1e6:.2f} Million" if fcf else None, "Q1 2025")

ev = valuation.get("EnterpriseValue")
ev_fcf = ev / fcf if ev and fcf else None
add_metric("EV/FCF", round(ev_fcf, 2) if ev_fcf else None, "Q1 2025")
add_metric("EV/EBITDA", valuation.get("EnterpriseValueEbitda"), "TTM")

# ROIC
net_income = highlights.get("NetIncomeTTM")
total_equity = bs_q.get("totalStockholderEquity")
total_debt = bs_q.get("shortLongTermDebtTotal")
if net_income and total_equity and total_debt:
    invested_capital = total_equity + total_debt
    roic = net_income / invested_capital * 100 if invested_capital else None
    add_metric("ROIC", f"{roic:.2f}%", "TTM")
else:
    add_metric("ROIC", None, "TTM")

add_metric("ROE", f"{highlights.get('ReturnOnEquityTTM') * 100:.2f}%" if highlights.get('ReturnOnEquityTTM') else None, "TTM")
add_metric("ROA", f"{highlights.get('ReturnOnAssetsTTM') * 100:.2f}%" if highlights.get('ReturnOnAssetsTTM') else None, "TTM")
add_metric("PEG (Trailing)", valuation.get("PEGRatio"), "TTM")
add_metric("PEG (Forward)", valuation.get("ForwardPEGRatio"), "TTM")
add_metric("EPS", highlights.get("EarningsShare"), "TTM")

mc = valuation.get("Market_Capitalization")
add_metric("Market Cap", f"${mc/1e9:.2f} Billion" if mc else None, "Q1 2025")
add_metric("Revenue", f"${income_q.get('totalRevenue')/1e6:.2f} Million" if income_q.get('totalRevenue') else None, "Q1 2025")
add_metric("Gross Profit", f"${income_q.get('grossProfit')/1e6:.2f} Million" if income_q.get('grossProfit') else None, "Q1 2025")

# Debt / Equity
if bs_q.get("totalLiab") and bs_q.get("totalStockholderEquity"):
    debt_equity = bs_q["totalLiab"] / bs_q["totalStockholderEquity"]
    add_metric("Debt / Equity", f"{debt_equity:.2f}", "Q1 2025")
else:
    add_metric("Debt / Equity", None, "Q1 2025")

add_metric("Enterprise Value", f"${ev/1e9:.2f} Billion" if ev else None, "Q1 2025")
add_metric("Dividend Yield", highlights.get("DividendYield") or "NONE", "Q1 2025")
add_metric("Payout Ratio", highlights.get("PayoutRatio") or "NONE", "Q1 2025")

# --- Display Table ---
st.subheader("📊 Key Financial Metrics")
st.dataframe({"Metric": [m[0] for m in metrics], "Value": [m[1] for m in metrics], "Period": [m[2] for m in metrics]})

# --- Moat Analysis ---
st.subheader("🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
st.markdown("""
Perimeter Solutions appears to possess elements of a **narrow economic moat** due to:

- **Specialized Niche**: The company is one of very few global providers of wildfire retardants and foams, operating under long-term contracts with federal agencies like the U.S. Forest Service.
- **High Switching Costs**: Governments and municipalities are unlikely to switch suppliers easily due to safety, approval, and logistic constraints — giving PRM a defensible position.
- **Regulatory Barriers**: Fire retardant products often require certifications and lengthy compliance processes, reducing new entrant threats.
- **R&D and IP**: The specialty chemicals segment relies on unique formulations and expertise in phosphorus pentasulfide-based additives, which provides technical differentiation.

**Weaknesses:**
- Low ROIC and lack of strong FCF indicate some operational inefficiencies.
- Revenue is highly seasonal and tied to wildfire activity — making cash flows unpredictable.

**Conclusion**: PRM exhibits a **narrow moat**, driven primarily by its regulatory entrenchment and mission-critical products, though financials (e.g., FCF and ROIC) do not yet reinforce long-term economic power.
""")
