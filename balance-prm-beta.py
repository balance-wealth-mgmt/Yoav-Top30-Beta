import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="PRM.US Financial Overview", layout="wide")

# Load API token from Streamlit secrets
api_token = st.secrets["eodhd"]["api_key"]

symbol = "PRM.US"
base_url = "https://eodhd.com/api/fundamentals/{}?api_token={}&fmt=json".format(symbol, api_token)
fundamentals = requests.get(base_url).json()

# Extract required sections
general = fundamentals.get("General", {})
highlights = fundamentals.get("Highlights", {})
valuation = fundamentals.get("Valuation", {})
ratios = fundamentals.get("Financials", {}).get("Ratios", {}).get("annual", {})
cashflow = fundamentals.get("Financials", {}).get("Cash_Flow", {}).get("quarterly", {})
income = fundamentals.get("Financials", {}).get("Income_Statement", {}).get("quarterly", {})
balance = fundamentals.get("Financials", {}).get("Balance_Sheet", {}).get("quarterly", {})

# Extract specific values
data_date = list(cashflow.keys())[0] if cashflow else "N/A"
revenue = float(income[data_date]["totalRevenue"]) if income and data_date in income else None
gross_profit = float(income[data_date]["grossProfit"]) if income and data_date in income else None
free_cash_flow = float(cashflow[data_date]["freeCashFlow"]) if cashflow and data_date in cashflow else None
total_debt = float(balance[data_date]["shortLongTermDebtTotal"]) if balance and data_date in balance else None
total_equity = float(balance[data_date]["totalStockholderEquity"]) if balance and data_date in balance else None

de_ratio = round(total_debt / total_equity, 2) if total_debt and total_equity else None
ev = float(valuation.get("EnterpriseValue", 0))
ev_fcf = round(ev / free_cash_flow, 2) if ev and free_cash_flow else None

eps = float(highlights.get("EarningsShare", 0))
roe = float(highlights.get("ReturnOnEquityTTM", 0))
roa = float(highlights.get("ReturnOnAssetsTTM", 0))
pe = float(valuation.get("TrailingPE", 0))
pb = float(valuation.get("PriceBookMRQ", 0))
ev_ebitda = float(valuation.get("EnterpriseValueEbitda", 0))
market_cap = float(highlights.get("MarketCapitalization", 0))
div_yield = highlights.get("DividendYield")
payout_ratio = highlights.get("PayoutRatio")
sector = general.get("Sector", "N/A")
industry = general.get("Industry", "N/A")
description = general.get("Description", "N/A")

# PEG estimates
growth_rate = float(ratios[data_date]["growthRatio"]["epsGrowth"]) if data_date in ratios else None
peg_trailing = round(pe / growth_rate, 2) if growth_rate else None
peg_forward = round((pe * eps) / growth_rate, 2) if eps and growth_rate else None

# ROIC Calculation
net_income = float(income[data_date]["netIncome"]) if data_date in income else None
roic = round(net_income / (total_debt + total_equity) * 100, 2) if net_income and total_debt and total_equity else None

# Assemble table data
data = {
    "Metric": [
        "Ticker", "Data's Date", "Industry", "Sector", "Description", "P/E", "P/B", "FCF", "EV/FCF", "EV/EBITDA",
        "ROIC", "ROE", "ROA", "PEG (Trailing)", "PEG (Forward)", "EPS", "Market Cap", "Revenue", "Gross Profit",
        "Debt / Equity", "Enterprise Value", "Dividend Yield", "Payout Ratio", "MOAT"
    ],
    "Value": [
        symbol, data_date, industry, sector, description, pe, pb,
        f"${free_cash_flow / 1e6:.2f} Million" if free_cash_flow else None,
        ev_fcf, ev_ebitda, f"{roic}%" if roic else None,
        f"{roe*100:.2f}%" if roe else None,
        f"{roa*100:.2f}%" if roa else None,
        peg_trailing, peg_forward, eps,
        f"${market_cap / 1e9:.2f} Billion" if market_cap else None,
        f"${revenue / 1e6:.2f} Million" if revenue else None,
        f"${gross_profit / 1e6:.2f} Million" if gross_profit else None,
        de_ratio, f"${ev / 1e9:.2f} Billion" if ev else None,
        f"{div_yield*100:.2f}%" if div_yield else "NONE",
        f"{payout_ratio*100:.2f}%" if payout_ratio else "NONE",
        "See Below"
    ],
    "Period": [
        "—", "Q1 2025", "Q1 2025", "Q1 2025", "—", "TTM", "Q1 2025", "Q1 2025", "Q1 2025", "TTM",
        "TTM", "TTM", "TTM", "TTM", "TTM", "TTM", "Q1 2025", "Q1 2025", "Q1 2025", "Q1 2025", "Q1 2025",
        "Q1 2025", "Q1 2025", "—"
    ]
}

df = pd.DataFrame(data)
st.title("Perimeter Solutions (PRM.US) – Financial Overview")
st.dataframe(df, use_container_width=True)

st.markdown("### 🛡️ MOAT Analysis: Perimeter Solutions (PRM.US)")
st.markdown("""
Perimeter Solutions appears to possess elements of a **narrow economic moat** due to:

- **Specialized Niche**: The company is one of very few global providers of wildfire retardants and foams, operating under long-term contracts with federal agencies like the U.S. Forest Service.
- **High Switching Costs**: Governments and municipalities are unlikely to switch suppliers easily due to safety, approval, and logistic constraints — giving PRM a defensible position.
- **Regulatory Barriers**: Fire retardant products often require certifications and lengthy compliance processes, reducing new entrant threats.
- **R&D and IP**: The specialty chemicals segment relies on unique formulations and expertise in phosphorus pentasulfide-based additives, which provides technical differentiation.

**Weaknesses**:
- Low ROIC and lack of strong FCF indicate some operational inefficiencies.
- Revenue is highly seasonal and tied to wildfire activity — making cash flows unpredictable.

**Conclusion**: PRM exhibits a narrow moat, driven primarily by its regulatory entrenchment and mission-critical products, though financials (e.g., FCF and ROIC) do not yet reinforce long-term economic power.
""")
