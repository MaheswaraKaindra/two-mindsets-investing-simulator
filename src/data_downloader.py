# src/data_downloader.py
# Kaindra

# IMPORTS
import yfinance as yf
import pandas as pd
import os

# STATIC DEFINITIONS
START_DATE                  = "2022-06-24"
END_DATE                    = "2025-06-25"

# FUNCTION DEFINITIONS
if not os.path.exists("data"):
    os.makedirs("data")

def get_tickers():
    """Getting user input for tickers."""
    input_tickers           = input("Input Stock Codes (comma separated), for example: BBCA, BBRI\n > ")

    # Default: BBCA and BBRI
    if not input_tickers.strip():
        print("Using default tickers: BBCA, BBRI")
        return ["BBCA.JK", "BBRI.JK"]
    
    # Handle: lower and upper case, and strip spaces
    tickers                 = [ticker.strip().upper() for ticker in input_tickers.split(",")]
    tickers_JK              = [f"{ticker}.JK" for ticker in tickers]

    # Return: list of tickers with .JK suffix
    print(f"Selected tickers: {', '.join(tickers_JK)}")
    return tickers_JK

def download_data(tickers, start = START_DATE, end = END_DATE):
    """Download stock data from Yahoo Finance and select 'Close' prices."""
    print(f"\nDownloading data for: {', '.join(tickers)}...")
    
    full_data = yf.download(tickers, start=start, end=end)
    
    # Handle: if no data is returned
    if full_data.empty:
        print("Failed to download data.")
        return pd.DataFrame()
    close_prices = full_data['Close']
    
    # Handle: if only one ticker is provided, convert Series to DataFrame
    if isinstance(close_prices, pd.Series):
        close_prices = close_prices.to_frame(name = tickers[0])

    print("Download successful.")
    return close_prices

def save_data_to_csv(close_data, tickers):
    """Save the close price data to separate CSV files."""
    
    # Handle: if close_data is empty
    if close_data.empty:
        print("No data to save.")
        return
    
    # Loop: through each ticker and save to CSV
    for ticker in tickers:
        if ticker in close_data.columns:
            file_name       = ticker.replace('.JK', '')
            file_path       = f"data/{file_name}.csv"

            stock_series    = close_data[ticker].dropna()

            # Handle: if the stock series is empty after dropping NaN values
            if stock_series.empty:
                print(f"No data available for {ticker} in the selected date range.")
                continue
            stock_series.to_csv(file_path, header=['Close'], index_label='Date')
            print(f"Data for {ticker} successfully saved to: {file_path}")
        
        else:
            print(f"Warning: Ticker '{ticker}' not found after download. It might be an invalid code.")

if __name__ == "__main__":
    tickers_to_download     = get_tickers()
    close_data              = download_data(tickers_to_download, start = START_DATE, end = END_DATE)
    if not close_data.empty:
        save_data_to_csv(close_data, tickers_to_download)