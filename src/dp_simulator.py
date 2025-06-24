# src/dp_simulator.py
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
def run_dp_simulations(data_folder="data", initial_capital=10000000):
    """
    Run Dynamic Programming simulation on all stocks in the data folder.
    
    Args:
        data_folder (str): Path to the folder containing CSV files.
        initial_capital (float): Initial capital for trading.
    
    Returns:
        tuple: (results_dict, stock_data_dict) where results_dict contains portfolio series 
               and stock_data_dict contains the original stock data for plotting.
    """
    all_stock_data = load_all_stock_data(data_folder)
    results        = {}
    
    for stock_code, stock_df in all_stock_data.items():
        print(f"\n{'='*50}")
        print(f"Running Dynamic Programming simulation for {stock_code}")
        print(f"{'='*50}")
        
        portfolio_values = dynamic_programming_simulator(stock_df, initial_capital)
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

def dynamic_programming_simulator(stock_data, initial_capital=10000000):
    """
    Simulate a patient investment strategy using Dynamic Programming approach.

    Heuristic:
    Build optimal solution step by step (forward) based on Optimality Principle.
    At each day (stage), the program calculates the maximum portfolio value
    that can be achieved for each possible state (holding stock or cash)
    by referring to the optimal value from the previous day.

    Args:
        stock_data (pd.DataFrame): DataFrame containing daily stock price data.
        initial_capital (float): Initial capital for simulation.

    Returns:
        pd.Series: A Series containing the optimal portfolio value history for each day.
    """
    print("Running Dynamic Programming strategy...")
    
    prices = stock_data['Close']
    n = len(prices)
    
    if n < 2:
        return pd.Series([initial_capital] * n, index=stock_data.index)

    # Initialize two arrays to store optimal values for each state
    # cash[i]: Maximum portfolio value on day i if ending with CASH
    # hold[i]: Maximum portfolio value on day i if ending with HOLDING STOCK
    cash = np.zeros(n)
    hold = np.zeros(n)

    # Initial Condition (Stage 0)
    cash[0] = initial_capital
    hold[0] = -float('inf') # Impossible to hold stock initially without buying

    # Loop: Forward Calculation (from day 1 to end)
    for i in range(1, n):
        price_today = prices.iloc[i]
        
        # Best value if holding CASH today:
        # Option 1: Do nothing (same value as cash yesterday)
        # Option 2: Sell stock held yesterday (hold value yesterday + today's selling price)
        cash[i] = max(cash[i-1], hold[i-1] + price_today)
        
        # Best value if holding STOCK today:
        # Option 1: Do nothing (same value as hold yesterday)
        # Option 2: Buy stock with cash yesterday (cash value yesterday - today's buying price)
        hold[i] = max(hold[i-1], cash[i-1] - price_today)

    # Final portfolio value is the value in 'cash' state on the last day,
    final_value = cash[-1]
    print(f"Dynamic Programming simulation completed. Final equity: ${final_value:,.0f}")
    
    # This function returns the portfolio value history if we always end in cash position
    return pd.Series(cash, index=stock_data.index)