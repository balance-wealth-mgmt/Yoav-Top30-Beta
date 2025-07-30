import streamlit as st
import requests
import pandas as pd
import datetime

# Load API token from Streamlit secrets
eodhd_token = st.secrets["eodhd"]["api_key"]

# --- SETTINGS ---
ticker = "PRM.US"
base_url = "https://eodhd.com/api"

def get_fundamental_data():
    url = f"{base_url}/fundamentals/{ticker}?api_token={eodhd_token}&fmt=json"
    response = requests.get(url)
    return response.json()

def get_market_cap():
    url = f"{base_url}/fundamentals/{ticker}?api_token={eodhd_token}&filter=Valuation::Market_Capitalization&fmt=json"
    response = requests.get(url)
    return response.json()

def get_financial_value(filter_str):
    url = f"{base_url}/fundamentals/{ticker}?api_token={eodhd_token}&filter={filter_str}&fmt=json"
    response = requests.get(url)
    return response.json()

def calculate_ev_fcf(ev, fcf):
    try:
        return round(ev / fcf, 2) if fcf != 0 else None
    except:
        return None

def calculate_debt_equity(total_liabilities, total_equity):
    try:
        return round(total_liabilities / total_equity, 2)
    except:
        return None

def main():
    st.title("PRM.US Financial Metrics Dashboard")

    fundamentals = get_fundamental_data()

    # Extract base info
    general = fundamentals.get("General", {})
    valuation = fundamentals.get("Valuation", {})
    highlights = fundamentals.get("Highlights", {})
    financials = fundamentals.get("Financials", {})
    metrics = fundamentals.get("Metrics", {})

    latest_quarter = next(iter(financials.get("Income_Statement", {}).get("quarterly", {})), None)
    latest_balance = next(iter(financials.get("Balance_Sheet", {}).get("quarterly", {})), None)
    
    income_data = financials.get("Income_Statement", {}).get("quarterly", {}).get(latest_quarter, {})
    balance_data = financials.get("Balance_Sheet", {}).get("quarterly", {}).get(latest_balance, {})
    cashflow_data = financials.get("Cash_Flow", {}).get("quarterly", {}).get(latest_quarter, {})

    # Build the data table
    data = [
        ("Ticker", ticker, "—"),
        ("Data's Date", latest_quarter, "Q1 2025"),
        ("Industry", general.get("Industry"), "Q1 2025"),
        ("Sector", general.get("Sector"), "Q1 2025"),
        ("Description", general.get("Description"), "—"),
        ("P/E", highlights.get("PERatio"), "TTM"),
        ("P/B", highlights.get("PriceToBookRatio"), "Q1 2025"),
        ("FCF", f"${float(cashflow_data.get('FreeCashFlow', 0))/1e6:.2f} Million", "Q1 2025"),
        ("EV/FCF", calculate_ev_fcf(valuation.get("Enterprise_Value", 0), float(cashflow_data.get("FreeCashFlow", 0))), "Q1 2025"),
        ("EV/EBITDA", valuation.get("EVToEBITDA"), "TTM or Annualized"),
        ("ROIC", metrics.get("ReturnOnInvestedCapital"), "TTM"),
        ("ROE", highlights.get("ReturnOnEquityTTM"), "TTM"),
        ("ROA", highlights.get("ReturnOnAssetsTTM"), "TTM"),
        ("PEG (Trailing)", metrics.get("PEGRatio"), "TTM"),
        ("PEG (Forward)", metrics.get("PEGRatioForward"), "TTM"),
        ("EPS", highlights.get("EarningsShare"), "TTM"),
        ("Market Cap", f"${valuation.get('Market_Capitalization') / 1e9:.2f} Billion", "Q1 2025"),
        ("Revenue", f"${float(income_data.get('totalRevenue', 0))/1e6:.2f} Million", "Q1 2025"),
        ("Gross Profit", f"${float(income_data.get('grossProfit', 0))/1e6:.2f} Million", "Q1 2025"),
        ("Debt / Equity", calculate_debt_equity(float(balance_data.get("totalLiab", 0)), float(balance_data.get("totalStockholderEquity", 1))), "Q1 2025"),
        ("Enterprise Value", f"${valuation.get('Enterprise_Value') / 1e9:.2f} Billion", "Q1 2025"),
        ("Dividend Yield", highlights.get("DividendYield"), "Q1 2025"),
        ("Payout Ratio", highlights.get("PayoutRatio"), "Q1 2025"),
        ("MOAT", "See Below", "—"),
    ]

    df = pd.DataFrame(data, columns=["Metric", "Value", "Period"])
    st.dataframe(df, use_container_width=True)

    st.markdown("""
    ### 🧠 MOAT Analysis
    **PRM.US** operates in the specialty chemicals niche, specifically in firefighting products and phosphorus-based additives.
    Its moat may be characterized by:
    - **Specialization** in a highly regulated domain (fire retardants).
    - **Switching Costs** due to performance-critical applications.
    - **R&D focus**, protecting intellectual property.
    - However, it may lack strong **brand power** or **network effects**, making this a moderate moat.
    """)

if __name__ == "__main__":
    main()
