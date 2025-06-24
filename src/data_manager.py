# src/data_manager.py
# Kaindra

# IMPORTS
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# FUNCTION DEFINITIONS
def load_all_stock_data(data_folder="data"):
    """
    Load all CSV files from the data folder.
    
    Args:
        data_folder (str): Path to the folder containing CSV files.
    
    Returns:
        dict: Dictionary with stock codes as keys and DataFrames as values.
    """
    stock_data = {}
    csv_files  = glob.glob(os.path.join(data_folder, "*.csv"))
    
    for file_path in csv_files:
        # Extract stock code from filename
        filename   = os.path.basename(file_path)
        stock_code = filename.replace('.csv', '')
        
        # Load the CSV file
        try:
            df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
            stock_data[stock_code] = df
            print(f"Loaded data for {stock_code}: {len(df)} records")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return stock_data

def save_results_summary(results, output_file="results/simulation_summary.csv"):
    """
    Save simulation results summary to a CSV file.
    
    Args:
        results (dict): Dictionary with stock codes as keys and portfolio series as values.
        output_file (str): Path to save the summary CSV file.
    """
    # Create results directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    summary_data    = []
    initial_capital = 10000000  # Default initial capital
    
    for stock_code, portfolio_values in results.items():
        final_value  = portfolio_values.iloc[-1]
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        # Calculate maximum drawdown
        cumulative_max = portfolio_values.cummax()
        drawdown       = (portfolio_values - cumulative_max) / cumulative_max * 100
        max_drawdown   = drawdown.min()
        
        summary_data.append({
            'Stock_Code': stock_code,
            'Initial_Capital': initial_capital,
            'Final_Value': final_value,
            'Total_Return_Percent': total_return,
            'Max_Drawdown_Percent': max_drawdown,
            'Trading_Days': len(portfolio_values)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('Total_Return_Percent', ascending=False)
    summary_df.to_csv(output_file, index=False)
    
    print(f"\nResults summary saved to: {output_file}")
    return summary_df

def plot_portfolio_performance(results, stock_data_dict, output_folder="results"):
    """
    Create and save portfolio performance plots for all stocks.
    
    Args:
        results (dict): Dictionary with stock codes as keys and portfolio series as values.
        stock_data_dict (dict): Dictionary with stock codes as keys and stock DataFrames as values.
        output_folder (str): Folder to save the plot images.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Set the style for better-looking plots
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create individual plots for each stock
    for stock_code, portfolio_values in results.items():
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Stock Price and SMA
        stock_data      = stock_data_dict[stock_code]
        stock_data['SMA'] = stock_data['Close'].rolling(window=5).mean()
        
        ax1.plot(stock_data.index, stock_data['Close'], label='Stock Price', linewidth=2, alpha=0.8)
        ax1.plot(stock_data.index, stock_data['SMA'], label='SMA (5 days)', linewidth=2, alpha=0.8)
        ax1.set_title(f'{stock_code} - Stock Price and Moving Average', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price (IDR)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Portfolio Value Over Time
        ax2.plot(portfolio_values.index, portfolio_values.values, 
                label=f'{stock_code} Portfolio', linewidth=2, color='green', alpha=0.8)
        ax2.axhline(y=10000000, color='red', linestyle='--', alpha=0.7, label='Initial Capital')
        ax2.set_title(f'{stock_code} - Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Portfolio Value (IDR)', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Format y-axis to show values in millions
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        
        plt.tight_layout()
        
        # Save the plot
        filename = f'{stock_code}_portfolio_analysis.png'
        filepath = os.path.join(output_folder, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved individual analysis for {stock_code}: {filepath}")
        plt.close()
    
    # Create a combined comparison plot
    create_combined_portfolio_plot(results, output_folder)

def create_combined_portfolio_plot(results, output_folder="results"):
    """
    Create a combined plot showing all portfolio performances.
    
    Args:
        results (dict): Dictionary with stock codes as keys and portfolio series as values.
        output_folder (str): Folder to save the plot images.
    """
    plt.figure(figsize=(14, 8))
    
    initial_capital = 10000000
    colors          = sns.color_palette("husl", len(results))
    
    for i, (stock_code, portfolio_values) in enumerate(results.items()):
        # Calculate returns as percentage
        returns = ((portfolio_values - initial_capital) / initial_capital) * 100
        plt.plot(portfolio_values.index, returns, 
                label=f'{stock_code}', linewidth=2, color=colors[i], alpha=0.8)
    
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, label='Break-even')
    plt.title('Portfolio Performance Comparison - All Stocks', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Returns (%)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Add summary statistics as text
    stats_text = "Final Returns:\n"
    for stock_code, portfolio_values in results.items():
        final_return = ((portfolio_values.iloc[-1] - initial_capital) / initial_capital) * 100
        stats_text  += f"{stock_code}: {final_return:.2f}%\n"
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the combined plot
    filename = 'combined_portfolio_comparison.png'
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved combined comparison plot: {filepath}")
    plt.close()

def create_performance_summary_chart(results, output_folder="results"):
    """
    Create a bar chart showing the final returns for all stocks.
    
    Args:
        results (dict): Dictionary with stock codes as keys and portfolio series as values.
        output_folder (str): Folder to save the plot images.
    """
    initial_capital = 10000000
    stock_codes     = []
    returns         = []
    
    for stock_code, portfolio_values in results.items():
        final_return = ((portfolio_values.iloc[-1] - initial_capital) / initial_capital) * 100
        stock_codes.append(stock_code)
        returns.append(final_return)
    
    # Sort by returns
    sorted_data = sorted(zip(stock_codes, returns), key=lambda x: x[1], reverse=True)
    stock_codes, returns = zip(*sorted_data)
    
    plt.figure(figsize=(10, 6))
    colors = ['green' if r >= 0 else 'red' for r in returns]
    bars   = plt.bar(stock_codes, returns, color=colors, alpha=0.7)
    
    plt.title('Final Portfolio Returns by Stock', fontsize=14, fontweight='bold')
    plt.xlabel('Stock Code', fontsize=12)
    plt.ylabel('Total Return (%)', fontsize=12)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, return_val in zip(bars, returns):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -0.5),
                f'{return_val:.1f}%', ha='center', va='bottom' if height >= 0 else 'top')
    
    plt.tight_layout()
    
    # Save the chart
    filename = 'returns_summary_chart.png'
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved returns summary chart: {filepath}")
    plt.close()