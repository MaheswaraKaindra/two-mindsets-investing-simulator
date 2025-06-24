# src/greedy_simulator.py
# Kaindra

# IMPORTS
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .data_manager import load_all_stock_data

# FUNCTION DEFINITIONS
def run_greedy_simulations(data_folder="data", initial_capital=10000000, sma_window=5):
    """
    Run greedy simulation on all stocks in the data folder.
    
    Args:
        data_folder (str): Path to the folder containing CSV files.
        initial_capital (float): Initial capital for trading.
        sma_window (int): Window size for the Simple Moving Average.
    
    Returns:
        tuple: (results_dict, stock_data_dict) where results_dict contains portfolio series 
               and stock_data_dict contains the original stock data for plotting.
    """
    all_stock_data = load_all_stock_data(data_folder)
    results        = {}
    
    for stock_code, stock_df in all_stock_data.items():
        print(f"\n{'='*50}")
        print(f"Running simulation for {stock_code}")
        print(f"{'='*50}")
        
        portfolio_values = greedy_simulator(stock_df, initial_capital, sma_window)
        results[stock_code] = portfolio_values
        
        # Summary: initial and final portfolio values, total return
        initial_value = initial_capital
        final_value   = portfolio_values.iloc[-1]
        total_return  = ((final_value - initial_value) / initial_value) * 100
        
        print(f"\nSUMMARY for {stock_code}:")
        print(f"Initial Capital: {initial_value:,.2f}")
        print(f"Final Portfolio Value: {final_value:,.2f}")
        print(f"Total Return: {total_return:.2f}%")
    
    return results, all_stock_data

def greedy_simulator(stock_data, initial_capital=10000000, sma_window=5):
    """
    Simulate a greedy trading strategy on stock data.

    Heuristic:
        Trend-following strategy using Simple Moving Average (SMA).
        Buying the stock when the price graph gradient > 0 (there's a profit potential).
        Selling the stock when the price graph gradient < 0 (stop loss).
        
        Buy (if): 
            - The today's price is above the SMA.
            - We don't hold the stock.
        
        Sell (if):
            - The today's price is below the SMA.
            - We hold the stock.

    Args:
        stock_data (pd.DataFrame): DataFrame containing stock closing prices.
        initial_capital (float): Initial capital for trading.
        sma_window (int): Window size for the Simple Moving Average (SMA).

    Returns:
        pd.Series: Series containing the portfolio value over time.
    """

    data             = stock_data.copy()
    data['SMA']      = data['Close'].rolling(window=sma_window).mean()
    cash             = initial_capital
    shares           = 0
    portfolio_values = []

    # Loop: Trading Simulation (Iterate Daily)
    for i in range(len(data)):

        # Handle: if SMA is NaN, skip the iteration (for the first few days)
        if np.isnan(data['SMA'].iloc[i]):
            portfolio_values.append(initial_capital)
            continue

        price_today = data['Close'].iloc[i]
        sma_today   = data['SMA'].iloc[i]

        # Buy: If price is above SMA and we don't hold the stock, buy shares
        if price_today > sma_today and shares == 0:
            # Buy: Go all in
            shares_to_buy = cash // price_today
            cost          = shares_to_buy * price_today
            cash         -= cost
            shares       += shares_to_buy
            print(f"{data.index[i].date()}: Bought {shares_to_buy} shares at {price_today:.2f}, Cash left: {cash:.2f}")
        
        # Sell: If price is below SMA and we hold the stock, sell shares
        elif price_today < sma_today and shares > 0:
            # Sell: Go all out
            sale_value = shares * price_today
            cash      += sale_value
            print(f"{data.index[i].date()}: Sold {shares} shares at {price_today:.2f}, Cash now: {cash:.2f}")
            shares     = 0

        current_portfolio_value = cash + (shares * price_today)
        portfolio_values.append(current_portfolio_value)

    print(f"Final Portfolio Value: {portfolio_values[-1]:.2f}")
    return pd.Series(portfolio_values, index=data.index)
    return summary_df