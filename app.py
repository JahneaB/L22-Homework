# Name: [Jahnea]
# COP2080 - Programming Assignment 4: Streamlit Interactive Dashboard

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Crypto Tracker", layout="wide")

# --- API Integration & Caching ---
@st.cache_data(ttl=300)
def fetch_coin_list():
    """Fetches list of top coins to populate the dropdown."""
    try:
        # Simplified URL and parameters to avoid 422 errors
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,  # Reduced from 50 to 10
            "page": 1,
            "sparkline": "false"
        }
        response = requests.get(url, params=params)
        response.raise_for_status() # Check for errors FIRST
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to fetch coin list: {e}")
        return pd.DataFrame()
@st.cache_data(ttl=300)
def fetch_historical_data(coin_id, days):
    """Fetches historical price data for the time series chart."""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": "daily"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Parse prices into DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()

# --- Sidebar (User Input Widgets) ---
st.sidebar.header("Dashboard Settings")
coin_df = fetch_coin_list()

if not coin_df.empty:
    # Widget 1: Selectbox for choosing the coin
    selected_coin_name = st.sidebar.selectbox("Select a Cryptocurrency", coin_df['name'])
    selected_coin_id = coin_df[coin_df['name'] == selected_coin_name]['id'].values[0]
    
    # Widget 2: Slider for selecting time range
    days_range = st.sidebar.slider("Select Date Range (Days)", 7, 365, 30)

    # --- Main Dashboard Logic ---
    st.title(f"🚀 {selected_coin_name} Real-Time Insights")
    
    coin_info = coin_df[coin_df['id'] == selected_coin_id].iloc[0]

    # Component 1: Metrics/KPI Display
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"${coin_info['current_price']:,}")
    col2.metric("Market Cap Rank", f"#{coin_info['market_cap_rank']}")
    col3.metric("24h Change", f"{coin_info['price_change_percentage_24h']:.2f}%", 
                delta_color="normal")

    # Component 2: Time Series Chart (Required)
    st.subheader(f"Price Trend (Last {days_range} Days)")
    hist_df = fetch_historical_data(selected_coin_id, days_range)
    if not hist_df.empty:
        st.line_chart(hist_df.set_index('timestamp'))

    # Component 3: Data Table
    st.subheader("Top 10 Market Comparison")
    st.dataframe(coin_df[['market_cap_rank', 'name', 'symbol', 'current_price', 'market_cap']].head(10), use_container_width=True)

else:
    st.warning("Please wait for API data to load or refresh the page.")