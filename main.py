# main.py
# Kaindra

# IMPORTS
from src.data_downloader import save_data_to_csv, get_tickers, download_data
from src.greedy_simulator import run_greedy_simulations
from src.dp_simulator import run_dp_simulations
from src.data_manager import save_results_summary, plot_portfolio_performance, create_performance_summary_chart
import os
import shutil

# FUNCTION DEFINITIONS
def clear_folders():
    """
    Clear all data in the data and results folders.
    """
    folders_to_clear = ["data", "results", "results/greedy", "results/dp"]
    
    for folder in folders_to_clear:
        if os.path.exists(folder):
            print(f"Clearing {folder} folder...")
            shutil.rmtree(folder)
            print(f"{folder} folder cleared.")
    
    # Recreate the folder structure
    folders_to_create = ["data", "results", "results/greedy", "results/dp"]
    for folder in folders_to_create:
        os.makedirs(folder, exist_ok=True)
        print(f"{folder} folder created.")

def print_comparison_summary(greedy_results, dp_results):
    """
    Print a detailed comparison between Greedy and Dynamic Programming results.
    
    Args:
        greedy_results (dict): Results from greedy algorithm
        dp_results (dict): Results from dynamic programming algorithm
    """
    print("\n" + "="*80)
    print("ALGORITHM COMPARISON SUMMARY")
    print("="*80)
    
    initial_capital = 10000000
    
    print(f"{'Stock':<8} {'Greedy Final':<15} {'Greedy Return':<12} {'DP Final':<15} {'DP Return':<12} {'Better':<10}")
    print("-" * 80)
    
    greedy_total = 0
    dp_total = 0
    
    for stock_code in greedy_results.keys():
        if stock_code in dp_results:
            greedy_final = greedy_results[stock_code].iloc[-1]
            dp_final = dp_results[stock_code].iloc[-1]
            
            greedy_return = ((greedy_final - initial_capital) / initial_capital) * 100
            dp_return = ((dp_final - initial_capital) / initial_capital) * 100
            
            better = "DP" if dp_final > greedy_final else "Greedy"
            
            print(f"{stock_code:<8} {greedy_final:<15,.0f} {greedy_return:<12.2f}% {dp_final:<15,.0f} {dp_return:<12.2f}% {better:<10}")
            
            greedy_total += greedy_final
            dp_total += dp_final
    
    print("-" * 80)
    greedy_avg_return = ((greedy_total/len(greedy_results) - initial_capital) / initial_capital) * 100
    dp_avg_return = ((dp_total/len(dp_results) - initial_capital) / initial_capital) * 100
    
    print(f"{'AVERAGE':<8} {greedy_total/len(greedy_results):<15,.0f} {greedy_avg_return:<12.2f}% {dp_total/len(dp_results):<15,.0f} {dp_avg_return:<12.2f}% {'DP' if dp_avg_return > greedy_avg_return else 'Greedy':<10}")
    
    overall_winner = "Dynamic Programming" if dp_avg_return > greedy_avg_return else "Greedy Algorithm"
    print(f"\nOVERALL WINNER: {overall_winner}")

def main():
    # Clear data and results folders at startup
    print("Clearing previous data and results...")
    clear_folders()
    
    data_folder = "data"
    
    # Input: user choice between top 5 IHSG stocks or custom input
    print("="*60)
    print("STOCK SELECTION")
    print("="*60)
    stock_choice = input("\nChoose stock option:\n1. Use top 5 IHSG stocks (BBCA, BBRI, BREN, BYAN, BMRI)\n2. Enter your own stock codes\nEnter your choice (1 or 2): ").strip()
    
    if stock_choice == "1":
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

    # Input: user choice for algorithm
    print("\n" + "="*60)
    print("ALGORITHM SELECTION")
    print("="*60)
    algorithm_choice = input("\nChoose algorithm:\n1. Greedy Algorithm (SMA-based trend following)\n2. Dynamic Programming (optimal buy-sell strategy)\n3. Run both algorithms for comparison\nEnter your choice (1, 2, or 3): ").strip()
    
    results = {}
    stock_data_dict = {}
    
    if algorithm_choice == "1":
        # Run only Greedy Algorithm
        print("\nRunning Greedy Algorithm simulation on all stock data...")
        results, stock_data_dict = run_greedy_simulations(data_folder)
        algorithm_name = "Greedy"
        
        # Save results to greedy folder
        save_results_summary(results, "results/greedy/simulation_summary.csv")
        plot_portfolio_performance(results, stock_data_dict, "results/greedy")
        create_performance_summary_chart(results, "results/greedy")
        
    elif algorithm_choice == "2":
        # Run only Dynamic Programming
        print("\nRunning Dynamic Programming simulation on all stock data...")
        results, stock_data_dict = run_dp_simulations(data_folder)
        algorithm_name = "Dynamic Programming"
        
        # Save results to dp folder
        save_results_summary(results, "results/dp/simulation_summary.csv")
        plot_portfolio_performance(results, stock_data_dict, "results/dp")
        create_performance_summary_chart(results, "results/dp")
        
    elif algorithm_choice == "3":
        # Run both algorithms
        print("\nRunning both algorithms for comparison...")
        
        print("\n" + "="*50)
        print("GREEDY ALGORITHM RESULTS")
        print("="*50)
        greedy_results, stock_data_dict = run_greedy_simulations(data_folder)
        
        print("\n" + "="*50)
        print("DYNAMIC PROGRAMMING RESULTS")
        print("="*50)
        dp_results, _ = run_dp_simulations(data_folder)
        
        # Combine results for comparison
        results = {
            'Greedy': greedy_results,
            'Dynamic Programming': dp_results
        }
        algorithm_name = "Both Algorithms"
        
        # Save individual summaries
        save_results_summary(greedy_results, "results/greedy/simulation_summary.csv")
        save_results_summary(dp_results, "results/dp/simulation_summary.csv")
        
        # Generate individual charts
        plot_portfolio_performance(greedy_results, stock_data_dict, "results/greedy")
        plot_portfolio_performance(dp_results, stock_data_dict, "results/dp")
        create_performance_summary_chart(greedy_results, "results/greedy")
        create_performance_summary_chart(dp_results, "results/dp")
        
        # Print detailed comparison
        print_comparison_summary(greedy_results, dp_results)
        return
    
    else:
        print("Invalid choice. Defaulting to Greedy Algorithm.")
        print("\nRunning Greedy Algorithm simulation on all stock data...")
        results, stock_data_dict = run_greedy_simulations(data_folder)
        algorithm_name = "Greedy"
        
        # Save results to greedy folder
        save_results_summary(results, "results/greedy/simulation_summary.csv")
        plot_portfolio_performance(results, stock_data_dict, "results/greedy")
        create_performance_summary_chart(results, "results/greedy")
    
    # Output: overall summary for selected algorithm (only for single algorithm runs)
    if algorithm_choice in ["1", "2"] or (algorithm_choice not in ["1", "2", "3"]):
        print("\n" + "="*70)
        print(f"OVERALL SUMMARY FOR ALL STOCKS ({algorithm_name.upper()} ALGORITHM)")
        print("="*70)
        
        # Loop: through results and print final values and returns
        for stock_code, portfolio_values in results.items():
            initial_value = 10000000  # Default initial capital
            final_value   = portfolio_values.iloc[-1]
            total_return  = ((final_value - initial_value) / initial_value) * 100
            print(f"{stock_code}: Final Value: {final_value:,.2f}, Return: {total_return:.2f}%")

if __name__ == "__main__":
    main()