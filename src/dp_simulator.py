# src/dp_simulator.py
# Kaindra

# IMPORTS
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import functools
from .data_manager import load_all_stock_data

# FUNCTION DEFINITIONS
def process_single_stock_dp(args):
    """
    Process a single stock with Dynamic Programming algorithm.
    
    Args:
        args (tuple): (stock_code, stock_df, initial_capital)
    
    Returns:
        tuple: (stock_code, portfolio_values)
    """
    stock_code, stock_df, initial_capital = args
    
    portfolio_values = dynamic_programming_simulator(stock_df, initial_capital)
    
    return stock_code, portfolio_values

def run_dp_simulations(data_folder="data", initial_capital=10000000, use_multiprocess=False):
    """
    Run Dynamic Programming simulation on all stocks in the data folder sequentially.
    
    Args:
        data_folder (str): Path to the folder containing CSV files.
        initial_capital (float): Initial capital for trading.
        use_multiprocess (bool): Legacy parameter, ignored (always runs sequentially).
    
    Returns:
        tuple: (results_dict, stock_data_dict) where results_dict contains portfolio series 
               and stock_data_dict contains the original stock data for plotting.
    """
    all_stock_data = load_all_stock_data(data_folder)
    results        = {}
    
    if not all_stock_data:
        return results, all_stock_data
    
    # Process each stock sequentially
    for stock_code, stock_df in all_stock_data.items():
        stock_code, portfolio_values = process_single_stock_dp(
            (stock_code, stock_df, initial_capital)
        )
        results[stock_code] = portfolio_values
    
    return results, all_stock_data

def dynamic_programming_simulator(stock_data, initial_capital=10000000):
    """
    Simulate investment strategy using Dynamic Programming approach.
    """
    print("Running DP strategy (Realistic model)...")
    
    prices = stock_data['Close'].to_numpy()
    n = len(prices)
    if n < 2:
        return pd.Series([initial_capital] * n, index=stock_data.index)

    # DYNAMIC PROGRAMMING APPROACH FOR ALL-IN TRADING

    # State variables for each day:
    # cash[i] = maximum cash we can have on day i (not holding any stock)
    # hold[i] = maximum value we can have on day i (holding stock)
    
    cash = np.zeros(n)
    hold = np.zeros(n)
    
    # Base case: Day 0
    cash[0] = initial_capital
    hold[0] = 0  # Can't hold stock on day 0 without buying
    
    # Forward pass: Calculate optimal values for all-in trading
    for i in range(1, n):
        price = prices[i]
        prev_price = prices[i-1]
        
        # Option 1: Stay in cash (no action)
        cash_stay = cash[i-1]
        
        # Option 2: Sell all holdings (if we had any)
        cash_sell = 0
        if hold[i-1] > 0:
            # Value of holdings adjusts with price change
            cash_sell = hold[i-1] * price / prev_price
        
        cash[i] = max(cash_stay, cash_sell)
        
        # Option 1: Keep holding (value adjusts with price)
        hold_keep = 0
        if hold[i-1] > 0:
            hold_keep = hold[i-1] * price / prev_price
        
        # Option 2: Buy all-in with yesterday's cash
        hold_buy = cash[i-1]
        
        hold[i] = max(hold_keep, hold_buy)
    
    # RECONSTRUCT OPTIMAL PATH
    # Work backwards to find the actual buy/sell sequence
    transactions = []
    i = n - 1
    
    # Determine final state - choose the better option
    if cash[n-1] > hold[n-1]:
        current_state = 'cash'
    else:
        current_state = 'hold'
        # Add final sell transaction
        transactions.append(('sell', n-1, prices[n-1]))
    
    while i > 0:
        price = prices[i]
        prev_price = prices[i-1]
        
        if current_state == 'cash':
            # Check if we got here by selling
            if hold[i-1] > 0:
                cash_from_sell = hold[i-1] * price / prev_price
                if abs(cash[i] - cash_from_sell) < abs(cash[i] - cash[i-1]):
                    transactions.append(('sell', i, price))
                    current_state = 'hold'
        else:  # current_state == 'hold'
            # Check if we got here by buying
            if abs(hold[i] - cash[i-1]) < 1e-6:
                transactions.append(('buy', i, price))
                current_state = 'cash'
        i -= 1
    
    transactions.reverse()
    
    # SIMULATE ACTUAL TRADING
    current_cash = initial_capital
    current_shares = 0
    portfolio_values = [initial_capital]
    
    transaction_idx = 0
    
    for i in range(1, n):
        price = prices[i]
        date_str = stock_data.index[i].strftime('%Y-%m-%d')
        
        if transaction_idx < len(transactions) and transactions[transaction_idx][1] == i:
            action, day, transaction_price = transactions[transaction_idx]
            
            if action == 'buy' and current_shares == 0:
                # Buy as many shares as possible
                shares_to_buy = current_cash // price
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    current_cash -= cost
                    current_shares += shares_to_buy
                    print(f"{date_str}: Bought {shares_to_buy:.0f} shares at {price:.2f}, Cash left: {current_cash:.2f}")
            
            elif action == 'sell' and current_shares > 0:
                # Sell all shares
                sale_value = current_shares * price
                current_cash += sale_value
                print(f"{date_str}: Sold {current_shares:.0f} shares at {price:.2f}, Cash now: {current_cash:.2f}")
                current_shares = 0
            
            transaction_idx += 1
        
        # Calculate portfolio value (cash + stock value)
        portfolio_value = current_cash + (current_shares * price)
        portfolio_values.append(portfolio_value)
    
    # Sell any remaining shares at the end
    if current_shares > 0:
        final_price = prices[-1]
        sale_value = current_shares * final_price
        current_cash += sale_value
        date_str = stock_data.index[-1].strftime('%Y-%m-%d')
        print(f"{date_str}: Final sale - Sold {current_shares:.0f} shares at {final_price:.2f}, Final cash: {current_cash:.2f}")
        portfolio_values[-1] = current_cash

    final_value = portfolio_values[-1]
    print(f"Final Portfolio Value: {final_value:,.0f}")
    print(f"Total Return: {((final_value / initial_capital) - 1) * 100:.2f}%")
    
    return pd.Series(portfolio_values, index=stock_data.index)