import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def calculate_performance_metrics(trades, initial_capital=100000):
    """Generates strategy performance analytics summary, regime analysis, and monthly vectors."""
    trades['Datetime'] = pd.to_datetime(trades['EntryDate'])
    trades['Month'] = trades['Datetime'].dt.strftime('%Y-%m-%d')
    trades['Is_Expiry'] = trades['Datetime'].dt.day_name() == 'Wednesday'

    # Consider initial capital and calculate NAV
    trades['NAV'] = 100 * (trades['AvailableCapital'] / initial_capital)

    # Calculate Peak NAV and Drawdown
    trades['Peak_NAV'] = trades['NAV'].cummax()
    trades['Drawdown'] = (trades['NAV'] - trades['Peak_NAV']) / trades['Peak_NAV']
    max_drawdown = trades['Drawdown'].min()

    # Calculate CAGR
    days_in_backtest = (trades['Datetime'].max() - trades['Datetime'].min()).days
    cagr = ((trades['NAV'].iloc[-1] / 100) ** (365.25 / days_in_backtest) - 1) if days_in_backtest > 0 else ((trades['NAV'].iloc[-1] / 100) - 1)

    # Determine win/loss statistics
    def get_win_stats(df):
        total = len(df)
        if total == 0: return 0, 0, 0.0, 0.0
        winners = len(df[df['GrossPnL'] > 0])
        losers = len(df[df['GrossPnL'] <= 0])
        return winners, losers, winners/total, losers/total

    ce_w, ce_l, ce_wp, ce_lp = get_win_stats(trades[trades['OptionTicker'] == 'CE'])
    pe_w, pe_l, pe_wp, pe_lp = get_win_stats(trades[trades['OptionTicker'] == 'PE'])
    tot_w, tot_l, tot_wp, tot_lp = get_win_stats(trades)

    # Calculate average PnL% for CE and PE on Expiry and Non-Expiry days
    trades['Trade_PnL%'] = trades['GrossPnL'] / trades['EntryValue']
    avg_pnl_stats = trades.groupby(['OptionTicker', 'Is_Expiry'])['Trade_PnL%'].mean().unstack()
    avg_pnl_stats.columns = ['Non-Expiry_Avg_PnL%', 'Expiry_Avg_PnL%']
    avg_pnl_stats.loc['Combined'] = trades.groupby('Is_Expiry')['Trade_PnL%'].mean().values
    avg_pnl_stats = (avg_pnl_stats * 100).round(2).astype(str) + '%'

    # Calculate monthly PnL%
    monthly_nav = trades.groupby('Month')['NAV'].last()
    monthly_pct_pnl = monthly_nav.pct_change().fillna((monthly_nav / 100) - 1) * 100
    monthly_pnl_df = monthly_pct_pnl.reset_index().rename(columns={'NAV': 'Monthly % P&L'})
    monthly_pnl_df['Monthly % P&L'] = monthly_pnl_df['Monthly % P&L'].round(2).astype(str) + '%'

    # Compile statistics summary
    stats_summary = pd.DataFrame({
        'Metric': ['CAGR', 'Max Drawdown', 'Total Winners', 'Total Losers', 'Total Win %', 'Total Loss %', 
                   'CE Winners', 'CE Losers', 'CE Win %', 'CE Loss %', 'PE Winners', 'PE Losers', 'PE Win %', 'PE Loss %'],
        'Value': [f"{cagr*100:.2f}%", f"{max_drawdown*100:.2f}%", tot_w, tot_l, f"{tot_wp*100:.2f}%", f"{tot_lp*100:.2f}%",
                  ce_w, ce_l, f"{ce_wp*100:.2f}%", f"{ce_lp*100:.2f}%", pe_w, pe_l, f"{pe_wp*100:.2f}%", f"{pe_lp*100:.2f}%"]
    })

    return stats_summary, avg_pnl_stats, monthly_pnl_df

def generate_performance_plots(trades, output_dir='outputs/'):
    """Renders equity vector trajectory charts and localized drawdown boundaries."""
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(12, 8))
    plt.plot(trades['Datetime'], trades['NAV'], color='blue', label='Equity Curve')
    plt.title('Equity Curve (Base NAV = 100)')
    plt.ylabel('NAV')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Equity_Plot.pdf'))
    plt.close()

    plt.figure(figsize=(12, 8))
    plt.plot(trades['Datetime'], trades['Drawdown'] * 100, color='red', label='Drawdown %')
    plt.title('Drawdown % from Peak NAV')
    plt.ylabel('Drawdown (%)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Drawdown_Plot.pdf'))
    plt.close()