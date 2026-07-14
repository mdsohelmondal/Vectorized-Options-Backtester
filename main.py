import time
import os
import pandas as pd
from src.data_loader import load_and_preprocess_data
from src.backtester import run_short_strangle_backtest
from src.analytics import calculate_performance_metrics, generate_performance_plots

def main():
    start_time = time.time()
    
    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)

    # 1. Data Ingestion Step
    print("Loading datasets dynamically...")
    data, spot_data = load_and_preprocess_data('data/Options_data_2023.csv', 'data/BANKNIFTY_SPOT.csv')
    time_load = time.time() - start_time
    print(f"Data Loaded. Time elapsed: {time_load:.2f} seconds")

    # 2. Pipeline Execution Step
    print("Executing backtesting strategy vectors...")
    trades = run_short_strangle_backtest(data, spot_data)
    time_trades = time.time() - start_time
    print(f"Trade Generation Complete. Time elapsed: {time_trades:.2f} seconds")

    # 3. Aggregated Analytics & Visualization Step
    print("Compiling statistical reports...")
    stats_summary, avg_pnl_stats, monthly_pnl_df = calculate_performance_metrics(trades)
    generate_performance_plots(trades, 'outputs/')
    time_stats = time.time() - start_time
    print(f"Statistics Calculated. Time elapsed: {time_stats:.2f} seconds")

    # 4. Multi-Sheet Spreadsheet Compilation Step
    excel_path = 'outputs/Qode_Backtest_Submission.xlsx'
    
    guide_content = pd.DataFrame({
        'Category': [
            '1. Assignment Objective', '2. Trading System Rules', '', '', '', '',
            '3. Data Context & Assumptions', '', '4. Known Data Limitations & Issues', '',
            '5. Worksheets Overview', '', '', ''
        ],
        'Details': [
            'Create a backtest for a Banknifty short strangle strategy that trades intraday, starting at 09:20 AM.',
            '- Strike Selection: At 09:20 AM, find the Call (CE) and Put (PE) options that have a price closest to Rs. 50.',
            '- Entry: Sell 1 lot (15 quantity) of both the CE and PE at the 09:20 AM closing price.',
            '- Stop Loss: A strict 50% stop loss is set for each option separately. If the 1-minute high price hits this stop loss, we exit that specific option.',
            '- Exit: Close any open positions at exactly 15:20 PM.',
            '- Position Sizing & Capital: Trade exactly 1 lot every day (no compounding). Initial Capital is set to Rs. 1,00,000 (1 Lakh).',
            "- Week 1 Data: The data given is assumed to be filtered for the week 1 data.",
            "- Expiry Day: The instructions treat Wednesday as the expiry day. I used this rule to separate the final statistics.",
            '- Spot Data Overlap: The Banknifty Spot data file only has data starting from October 20, 2023. But our main options data starts much earlier in the year.',
            "- What happens because of this: The 'BankniftyClose' column in the final sheet will be blank for the earlier months.",
            '- Guide: This sheet, which explains the rules and data.',
            '- Tradesheet: A detailed list of every single trade taken during the backtest.',
            '- Statistics: The overall performance results such as, CAGR, Max Drawdown, win rate, and month-by-month profits.',
            '- Execution Time: The calculation of the time for executing the script, broken down step-by-step in seconds.'
        ]
    })

    time_total = time.time() - start_time
    time_summary = pd.DataFrame({
        'Execution Step': ['Data Loading Complete', 'Trade Generation Complete', 'Statistics Calculated', 'Total Execution Time'],
        'Cumulative Time (Seconds)': [f"{time_load:.2f}", f"{time_trades:.2f}", f"{time_stats:.2f}", f"{time_total:.2f}"]
    })

    final_columns = [
        'Ticker', 'OptionTicker', 'EntryDate', 'EntryTime', 'EntryPrice', 'ExitDate', 
        'ExitTime', 'ExitPrice', 'BankniftyClose', 'LotQuantity', 'LotSize', 
        'StrikePrice', 'EntryValue', 'ExitValue', 'GrossPnL', 'CumulativePnL', 'AvailableCapital'
    ]

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        guide_content.to_excel(writer, sheet_name='Guide', index=False)
        trades[final_columns].to_excel(writer, sheet_name='Tradesheet', index=False)
        stats_summary.to_excel(writer, sheet_name='Statistics', index=False, startrow=0)
        avg_pnl_stats.reset_index().to_excel(writer, sheet_name='Statistics', index=False, startrow=len(stats_summary) + 2)
        monthly_pnl_df.to_excel(writer, sheet_name='Statistics', index=False, startrow=len(stats_summary) + len(avg_pnl_stats) + 4)
        time_summary.to_excel(writer, sheet_name='Execution Time', index=False)

        # Apply Worksheet column width auto-formatting adjustments
        worksheet_guide = writer.sheets['Guide']
        bold_format = writer.book.add_format({'bold': True, 'valign': 'top'})
        worksheet_guide.set_column(0, 0, 35, bold_format)
        wrap_format = writer.book.add_format({'text_wrap': True, 'valign': 'top'})
        worksheet_guide.set_column(1, 1, 110, wrap_format)

        worksheet_trades = writer.sheets['Tradesheet']
        for i, col in enumerate(final_columns):
            column_len = max(trades[col].astype(str).map(len).max(), len(col))
            worksheet_trades.set_column(i, i, column_len + 3)

        writer.sheets['Statistics'].set_column(0, 15, 25)
        
        worksheet_time = writer.sheets['Execution Time']
        worksheet_time.set_column(0, 0, 30)
        worksheet_time.set_column(1, 1, 25)

    print(f"Excel Export Complete. Total execution time: {time_total:.2f} seconds")

if __name__ == '__main__':
    main()