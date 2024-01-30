
#   Author: Andrew Nelson
#   Description: This program gets the market cap, revenue, PE ratio, PS ratio, and volatility for a list of tickers.
#   Date Created: 21-JAN-2024
#   Last Modified: 24-JAN-2024
#   Revision: 4.1

#Import all the things
import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys
import streamlit as st
import logging
from datetime import datetime, timedelta

# To helps suppress all unwanted outputs from yfinance
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Get the historical prices for this ticker
start_date = (datetime.now() - timedelta(days=366)).strftime('%Y-%m-%d')
end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# List of tickers from user and list to store the data
tickers = []
data = []

# Initialize a counter variable
key_counter = 0

# Streamlit code to get user input
tickers_input = st.text_input("Enter a ticker(s):", '', key=f'unique_{key_counter}')
key_counter += 1

# Where the magic happens
if st.button('Get Data'):

    # Split the input string into individual tickers
    tickers_input = tickers_input.replace(',', ' ')  # Replace commas with spaces
    tickers_input = tickers_input.split()  # Split the string into a list of tickers

    # Loop through each ticker, remove $ from the beginning, and append it to the tickers list
    for ticker in tickers_input:
        ticker = ticker.lstrip('$')
        tickers.append(ticker.upper())

    # Get the data for each ticker
    for ticker in tickers:  # Loop through each ticker to get the data
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get the market cap and format it as currency
        market_cap = round(info.get("marketCap", 0) / 1_000_000)
        if market_cap < 1000:  # If market cap is less than 1 billion
            market_cap = f"${format(market_cap, ',.2f')}M"  # Format as currency with commas and 2 decimal places
        else:
            market_cap = f"${format(market_cap, ',')}M"  # Format as currency with commas

        # Get the revenue and format it as currency
        revenue = round(info.get("totalRevenue", 0) / 1_000_000)
        revenue = f"${format(revenue, ',')}M"  # Format as currency with commas

        # Get the PE and PS ratios
        pe_ratio = "{:.2f}".format(info.get("trailingPE", 0))
        ps_ratio = "{:.2f}".format(info.get("priceToSalesTrailing12Months", 0))

        # Suppress all output from yfinance when getting 1 year of data
        stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        try:
            tickerDf = stock.history(raise_errors=False, start=start_date, end=end_date,)
        finally:
            sys.stderr = stderr

        # Calculate the daily returns
        tickerDf['Return'] = tickerDf['Close'].pct_change()

        # Calculate the annualized volatility
        volatility = tickerDf['Return'].std() * np.sqrt(252)  # There are typically 252 trading days in a year
        volatility = "{:.3f}".format(volatility)

        # Add the data to the list
        data.append([ticker, market_cap, revenue, pe_ratio, ps_ratio, volatility])
    
    st.write("") # Print a blank line

    # Print the data in a table
    df = pd.DataFrame(data, columns=["Ticker", "Market Cap", "Revenue", "PE Ratio", "PS Ratio", "Volatility"])
    st.table(df)
