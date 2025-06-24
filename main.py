# main.py
# Kaindra

# IMPORTS
from src.data_downloader import save_data_to_csv, get_tickers, download_data
from src.greedy_simulator import run_greedy_simulations
from src.data_manager import save_results_summary, plot_portfolio_performance, create_performance_summary_chart
import os
import shutil

# FUNCTION DEFINITIONS
def clear_folders():
    """
    Clear all data in the data and results folders.
    """
    folders_to_clear = ["data", "results"]
    
    for folder in folders_to_clear:
        if os.path.exists(folder):
            print(f"Clearing {folder} folder...")
            shutil.rmtree(folder)
            os.makedirs(folder)
            print(f"{folder} folder cleared and recreated.")
        else:
            print(f"Creating {folder} folder...")
            os.makedirs(folder)

def main():
    # Clear data and results folders at startup
    print("Clearing previous data and results...")
    clear_folders()
    
    data_folder = "data"
    
    # Input: user choice between top 5 IHSG stocks or custom input
    choice = input("\nChoose an option:\n1. Use top 5 IHSG stocks (BBCA, BBRI, BREN, BYAN, BMRI)\n2. Enter your own stock codes\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        # Option 1: Use top 5 IHSG stocks
        print("\nUsing top 5 IHSG stocks: BBCA, BBRI, BREN, BYAN, BMRI")
        tickers = ["BBCA.JK", "BBRI.JK", "BREN.JK", "BYAN.JK", "BMRI.JK"]
    else:
        # Option 2: Get user input for stock tickers
        print("Downloading custom stock data...")
        tickers = get_tickers()

    # Download stock data
    stock_data = download_data(tickers)

    # Handle: if no data is returned
    if stock_data.empty:
        print("No data available for the selected tickers.")
        return

    # Save the downloaded data to CSV files
    save_data_to_csv(stock_data, tickers)

    # Run simulations on all stock data
    print("\nRunning simulations on all stock data...")
    results, stock_data_dict = run_greedy_simulations(data_folder)
    
    # Save results summary
    save_results_summary(results)
    
    # Generate and save portfolio charts
    print("\nGenerating portfolio performance charts...")
    plot_portfolio_performance(results, stock_data_dict)
    create_performance_summary_chart(results)
    
    # Output: overall summary for all stocks
    print("\n" + "="*70)
    print("OVERALL SUMMARY FOR ALL STOCKS")
    print("="*70)
    
    # Loop: through results and print final values and returns
    for stock_code, portfolio_values in results.items():
        initial_value = 10000000  # Default initial capital
        final_value   = portfolio_values.iloc[-1]
        total_return  = ((final_value - initial_value) / initial_value) * 100
        print(f"{stock_code}: Final Value: {final_value:,.2f}, Return: {total_return:.2f}%")

if __name__ == "__main__":
    main()