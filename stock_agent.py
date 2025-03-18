import yfinance as yf
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta
from autogen import AssistantAgent
from autogen.tools import Tool

# Streamlit App Configuration
st.set_page_config(page_title="Stock Assistant", layout="wide")

# Function to Fetch and Display Stock Data
def fetch_stock_data(tickers: list, days: int = 7):
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        result_str = ""
        stock_data_dict = {}

        for ticker in tickers:
            data = yf.download(ticker, start=start_date, end=end_date)

            if data.empty:
                result_str += f"❌ No data found for {ticker}\n\n"
                continue

            stock_data_dict[ticker] = data
            formatted_data = data[['Open', 'High', 'Low', 'Close']]
            result_str += f"\n📈 Stock Data for {ticker} (Last {len(formatted_data)} days)\n"
            result_str += formatted_data.to_string() + f"\n\n📝 Note: Some days may be holidays or market closures.\n\n"

        return result_str, stock_data_dict

    except Exception as e:
        return str(e), {}

# Function to Extract Stock Tickers and Days from Input
def extract_info(user_input):
    tickers = re.findall(r"\b[A-Z]{1,5}\b", user_input)
    days_match = re.search(r"(\d+)\s*days", user_input)
    days = int(days_match.group(1)) if days_match else 7  # Default to 7 days
    return tickers, days if tickers else (None, None)

# Initialize AutoGen Assistant
assistant = AssistantAgent(
    name="StockAssistant",
    system_message="I can fetch stock data and visualize it. Enter the stock tickers and duration.",
    code_execution_config={"use_docker": False}
)

# Register Stock Tool with Assistant
fetch_stock_tool = Tool(
    name="fetch_stock_data",
    description="Fetches stock data for given tickers over a specified number of days.",
    func_or_tool=fetch_stock_data
)

# Streamlit UI Layout
st.title("📊 Stock Data Assistant")
st.sidebar.header("⚙️ Input Settings")

# User Inputs
user_input = st.sidebar.text_input("Enter Stock Tickers (comma-separated)", "AAPL, TSLA")
tickers = [t.strip().upper() for t in user_input.split(",") if t.strip()]
days = st.sidebar.slider("Select Number of Days", 1, 30, 7)
response_type = st.sidebar.radio("Choose Response Type", ["Text", "Graph", "Both"])

# Fetch Data on Button Click
if st.sidebar.button("Fetch Stock Data"):
    if not tickers:
        st.sidebar.error("⚠️ Please enter at least one valid stock ticker.")
    else:
        response, stock_data_dict = fetch_stock_data(tickers, days)

        # Display Text Data
        if response_type in ["Text", "Both"]:
            st.subheader("📜 Stock Data Summary")
            st.text(response)

        # Display Graph
        if response_type in ["Graph", "Both"] and stock_data_dict:
            st.subheader("📉 Stock Price Visualization")
            fig, ax = plt.subplots(figsize=(10, 5))
            for ticker, data in stock_data_dict.items():
                ax.plot(data.index, data['Close'], label=ticker)

            ax.set_title("Stock Price Comparison")
            ax.set_xlabel("Date")
            ax.set_ylabel("Closing Price (USD)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
