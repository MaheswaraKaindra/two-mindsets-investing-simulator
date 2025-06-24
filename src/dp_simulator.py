# src/dp_simulator.py
# Kaindra

# IMPORTS
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from multiprocessing import Pool, cpu_count
import functools
from .data_manager import load_all_stock_data

# FUNCTION DEFINITIONS
def process_single_stock_dp(args):
    """
    Process a single stock with Dynamic Programming algorithm - helper function for multiprocessing.
    
    Args:
        args (tuple): (stock_code, stock_df, initial_capital)
    
    Returns:
        tuple: (stock_code, portfolio_values)
    """
    stock_code, stock_df, initial_capital = args
    
    portfolio_values = dynamic_programming_simulator(stock_df, initial_capital)
    
    return stock_code, portfolio_values

def run_dp_simulations(data_folder="data", initial_capital=10000000, use_multiprocess=True):
    """
    Run Dynamic Programming simulation on all stocks in the data folder using multiprocessing.
    
    Args:
        data_folder (str): Path to the folder containing CSV files.
        initial_capital (float): Initial capital for trading.
        use_multiprocess (bool): Whether to use multiprocessing for faster execution.
    
    Returns:
        tuple: (results_dict, stock_data_dict) where results_dict contains portfolio series 
               and stock_data_dict contains the original stock data for plotting.
    """
    all_stock_data = load_all_stock_data(data_folder)
    results        = {}
    
    if not all_stock_data:
        return results, all_stock_data
    
    if use_multiprocess and len(all_stock_data) > 1:
        num_processes = min(cpu_count(), len(all_stock_data))
        
        args_list = [(stock_code, stock_df, initial_capital) 
                    for stock_code, stock_df in all_stock_data.items()]
        
        with Pool(processes=num_processes) as pool:
            results_list = pool.map(process_single_stock_dp, args_list)
        
        for stock_code, portfolio_values in results_list:
            results[stock_code] = portfolio_values
            
    else:
        for stock_code, stock_df in all_stock_data.items():
            stock_code, portfolio_values = process_single_stock_dp(
                (stock_code, stock_df, initial_capital)
            )
            results[stock_code] = portfolio_values
    
    return results, all_stock_data

def dynamic_programming_simulator(stock_data, initial_capital=10000000):
    """
    Simulate a patient investor strategy using Dynamic Programming approach.

    Methodology:
    1. Analysis Phase (DP): Analyze all historical data to find
       one pair of buy and sell dates that provides maximum profit
       from a single transaction cycle.
    2. Simulation Phase: Run daily simulation where buy and sell
       actions are only executed on the optimal dates found.

    Args:
        stock_data (pd.DataFrame): DataFrame containing daily stock price data.
        initial_capital (float): Initial capital for simulation.

    Returns:
        pd.Series: A Series containing portfolio value history for each day.
    """
    print("Running Dynamic Programming strategy (Two-Phase method)...")
    
    prices = stock_data['Close']
    n = len(prices)
    
    if n < 2:
        print("Insufficient data for simulation.")
        return pd.Series([initial_capital] * n, index=stock_data.index)

    # === PHASE 1: Find Best Buy and Sell Days (DP Logic) ===
    min_price_so_far = float('inf')
    max_profit = 0
    best_buy_date = None
    best_sell_date = None
    
    # Variable to store temporary buy date when lowest price is found
    temp_buy_date = prices.index[0]

    for i in range(n):
        current_date = prices.index[i]
        current_price = prices.iloc[i]

        # If current price is lower than previous minimum, record as potential buy point
        if current_price < min_price_so_far:
            min_price_so_far = current_price
            temp_buy_date = current_date

        # Calculate potential profit if selling stock bought at minimum price today
        potential_profit = current_price - min_price_so_far

        # If this potential profit is the largest so far, save this transaction
        if potential_profit > max_profit:
            max_profit = potential_profit
            best_buy_date = temp_buy_date
            best_sell_date = current_date
            
    # If no profit can be made (price keeps falling)
    if best_buy_date is None:
        print("No profitable transaction opportunity found. No actions taken.")
        return pd.Series([initial_capital] * n, index=stock_data.index)
        
    print(f"Optimal transaction found: Buy on {best_buy_date.date()} & Sell on {best_sell_date.date()}")
    
    cash = initial_capital
    shares = 0
    portfolio_values = []

    for i in range(n):
        current_date = prices.index[i]
        price_today = prices.iloc[i]

        # Buy action only on the predetermined best day
        if current_date == best_buy_date:
            shares_to_buy = cash // price_today
            cost = shares_to_buy * price_today
            cash -= cost
            shares += shares_to_buy
            print(f"{current_date.strftime('%Y-%m-%d')}: Bought {shares_to_buy:.1f} shares at {price_today:.2f}, Cash left: {cash:.2f}")
        
        # Sell action only on the predetermined best day
        elif current_date == best_sell_date:
            sale_value = shares * price_today
            cash += sale_value
            print(f"{current_date.strftime('%Y-%m-%d')}: Sold {shares:.1f} shares at {price_today:.2f}, Cash now: {cash:.2f}")
            shares = 0
            
        # Calculate total portfolio value at the end of each day
        current_portfolio_value = cash + (shares * price_today)
        portfolio_values.append(current_portfolio_value)

    print(f"Final Portofolio Value: {portfolio_values[-1]:,.0f}")
    return pd.Series(portfolio_values, index=stock_data.index)