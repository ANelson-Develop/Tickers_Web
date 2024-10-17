
#   Author: Andrew Nelson
#   Description: This program gets the market cap, revenue, revenue growth, PE ratio, PS ratio, and volatility for a list of tickers.
#   Date Created: 21-JAN-2024
#   Last Modified: 17-OCT-2024
#   Revision: 4.9

#Import all the things
import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys
import streamlit as st
import logging
from datetime import datetime, timedelta

st.set_page_config(layout="wide")  # Set the page layout to wide

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
tickers_input = st.text_input("Enter ticker(s):", '', key=f'unique_{key_counter}')
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

        ticker_url = f"https://finance.yahoo.com/quote/{ticker}/"

        # Get the market cap and format it as currency
        market_cap = round(info.get("marketCap", 0) / 1_000_000,2)
        
        
        # Get the revenue and format it as currency
        revenue = round(info.get("totalRevenue", 0) / 1_000_000,2)
               
        #Get Revenue Growth
        revenue_growth = info.get("revenueGrowth")*100
        
        # Get the EBITDA and format it as currency
        ebitda = round(info.get("ebitda", 0) / 1_000_000,2)

        # Get the PE and PS ratios
        pe_ratio = info.get("trailingPE", 0)
        ps_ratio = info.get("priceToSalesTrailing12Months", 0)

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
        
        #Get Current Volume
        average_volume = info.get('averageDailyVolume10Day')

        # Add the data to the list
        data.append([ticker, market_cap, revenue, ebitda, pe_ratio, ps_ratio, volatility, revenue_growth,average_volume,ticker_url])

    st.write("") # Print a blank line

    # Create a dataframe from the data
    df = pd.DataFrame(data, columns=["Ticker","Market Cap", "Revenue","EBITDA", "PE Ratio", "PS Ratio", "Volatility", "YoY Growth","Avg Volume","Link"])
    


    # Format the dataframe 
    df_styled = df.style.format({
    'Market Cap': '${0:,.0f}M',
    'Revenue': '${0:,.0f}M',
    'EBITDA': '${0:,.0f}M',
    'PE Ratio': '{0:,.2f}',
    'PS Ratio': '{0:,.2f}',
    'YoY Growth': '{0:,.1f}%',
    'Avg Volume': '{0:,.0f}',
    })

    # Display the dataframe with clickable links
    st.dataframe(
        df_styled,
        column_config={
            "Link": st.column_config.LinkColumn(
                "Link",
                display_text="https://finance\.yahoo\.com/quote/(.*?)/" # Display the ticker as the link text
            ),
        },
        hide_index=True,
    )


