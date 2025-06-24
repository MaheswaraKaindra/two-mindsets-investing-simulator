# src/data_downloader.py
# Kaindra

# IMPORTS
import yfinance as yf
import pandas as pd
import os

# STATIC DEFINITIONS
START_DATE                  = "2022-06-24"
END_DATE                    = "2025-06-24"

# FUNCTION DEFINITIONS
if not os.path.exists("data"):
    os.makedirs("data")

def get_tickers():
    """Getting user input for tickers."""
    input_tickers           = input("Input Stock Codes (comma separated), for example: BBCA, BBRI\n > ")

    # Default: BBCA and BBRI
    if not input_tickers.strip():
        return ["BBCA.JK", "BBRI.JK"]
    
    # Handle: lower and upper case, and strip spaces
    tickers                 = [ticker.strip().upper() for ticker in input_tickers.split(",")]
    tickers_JK              = [f"{ticker}.JK" for ticker in tickers]

    # Return: list of tickers with .JK suffix
    print(f"Selected tickers: {', '.join(tickers_JK)}")
    return tickers_JK

def download_data(tickers, start = START_DATE, end = END_DATE):
    """Download stock data from Yahoo Finance."""
    data                    = yf.download(tickers, start = start, end = end)['Adj Close']

    # Handle: only one ticker is valid
    if isinstance(data, pd.Series):
        data                = data.to_frame(name = tickers[0])
    
    # Return: DataFrame with stock prices
    print(f"Downloaded data for {len(tickers)} ticker(s): {', '.join(tickers)}")
    return data

def save_data_to_csv(full_data, tickers):
    """Save the downloaded data to CSV files."""
    
    # Handle: full_data is empty
    if full_data.empty:
        print("No data to save.")
        return
    
    # Loop: through each ticker and save to CSV
    for ticker in tickers:
        if ticker in full_data.columns:
            file_name       = ticker.replace('.JK', '')
            file_path       = f"data/{file_name}.csv"

            stock_series    = full_data[ticker].dropna()

            # Handle: stock_series is empty
            if stock_series.empty:
                print(f"No data available for {ticker}. Skipping save.")
                continue

            stock_series.to_csv(file_path, header = ['Close'])
            print(f"Saved data for {ticker} to {file_path}")
        
        else:
            print(f"Ticker {ticker} not found in the downloaded data. Skipping save.")

if __name__ == "__main__":
    tickers_to_download     = get_tickers()
    full_data               = download_data(tickers_to_download, start = START_DATE, end = END_DATE)
    if not full_data.empty:
        save_data_to_csv(full_data, tickers_to_download)