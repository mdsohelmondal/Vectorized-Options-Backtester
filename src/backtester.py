import pandas as pd
import numpy as np

def run_short_strangle_backtest(data, spot_data, initial_capital=100000, lotsize=15):
    """Executes vectorized short strangle simulation including entry, exit, and risk bounds."""
    # Seggregate the 09:20:59 data and calculate distance from 50
    data920 = data[data['Time'] == '09:20:59'].copy()
    data920['Distance'] = abs(data920['Close'] - 50).abs()

    # Separate CE and PE data
    data920pe = data920[data920['Call/Put'] == 'PE'].copy()
    data920ce = data920[data920['Call/Put'] == 'CE'].copy()

    # Find the index of the minimum distance for CE and PE for each date
    min_dist_pe_index = data920pe.groupby('Date')['Distance'].idxmin()
    min_dist_ce_index = data920ce.groupby('Date')['Distance'].idxmin()

    # Keep only the rows with minimum distance for CE and PE
    min_dist_pe = data920pe.loc[min_dist_pe_index]
    min_dist_ce = data920ce.loc[min_dist_ce_index]

    pe_trades = min_dist_pe[['Date', 'Ticker', 'Close', 'Call/Put']].rename(columns={'Close': 'EntryPrice'})
    ce_trades = min_dist_ce[['Date', 'Ticker', 'Close', 'Call/Put']].rename(columns={'Close': 'EntryPrice'})

    # Combine CE and PE trades and sort by date
    trades = pd.concat([pe_trades, ce_trades], ignore_index=True)
    trades = trades.sort_values('Date').reset_index(drop=True)

    # Calculate Stop Loss limit
    trades['SL_Limit'] = (trades['EntryPrice'] * 1.5).round(2)

    # Filter the main data for the required time range of a day
    req_one_day_data = data[(data['Time'] >= '09:21:59') & (data['Time'] <= '15:20:59')].copy()

    # Merge the filtered data with the trades
    tracking_data = pd.merge(req_one_day_data, trades[['Date', 'Ticker', 'EntryPrice', 'SL_Limit']], on=['Date', 'Ticker'], how='inner')

    # Check if Stop Loss was hit
    tracking_data['SL_Hit'] = tracking_data['High'] >= tracking_data['SL_Limit']

    # Get the first instance of SL hit for each trade
    SL_exits = (tracking_data[tracking_data['SL_Hit']].groupby(['Date', 'Ticker']).first().reset_index()[['Date', 'Ticker', 'Time', 'Close']].rename(columns={'Time': 'Exit_Time', 'Close': 'Exit_Price'}))
    SL_exits['Exit_Reason'] = 'StopLoss'

    # Get the normal exit price and time at 15:20:59
    data1520 = data[data['Time'] == '15:20:59'][['Date', 'Ticker', 'Close', 'Time']].rename(
        columns={'Close': 'ExitPrice_Normal', 'Time': 'ExitTime_Normal'}
    )

    # Merge the SL exits and data at 15:20:59 with the trades
    trades = pd.merge(trades, SL_exits, on=['Date', 'Ticker'], how='left')
    trades = pd.merge(trades, data1520, on=['Date', 'Ticker'], how='left')

    # Determine the final exit price and time based on whether SL was hit or not
    trades['ExitPrice'] = np.where(trades['Exit_Reason'] == 'StopLoss', trades['Exit_Price'], trades['ExitPrice_Normal'])
    trades['ExitTime'] = np.where(trades['Exit_Reason'] == 'StopLoss', trades['Exit_Time'], trades['ExitTime_Normal'])
    trades['Exit_Reason'] = trades['Exit_Reason'].fillna('Normal')

    trades['LotSize'] = lotsize
    trades['EntryValue'] = (trades['EntryPrice'] * trades['LotSize']).round(2)
    trades['ExitValue'] = (trades['ExitPrice'] * trades['LotSize']).round(2)

    # Calculate Gross and cumulative PnL
    trades['GrossPnL'] = ((trades['EntryPrice'] - trades['ExitPrice']) * trades['LotSize']).round(2)
    trades['CumulativePnL'] = (trades['GrossPnL'].cumsum()).round(2)

    # Add additional columns
    trades['EntryDate'] = trades['Date']
    trades['ExitDate'] = trades['Date']
    trades['EntryTime'] = '09:20:59'
    trades['StrikePrice'] = trades['Ticker'].str.extract(r'(\d+)')[0]

    # Calculate Available Capital based on base
    trades['AvailableCapital'] = initial_capital + trades['CumulativePnL']

    # Merge the processed spot data to get BankniftyClose at exit time
    trades = pd.merge(trades, spot_data, left_on=['Date', 'ExitTime'], right_on=['Date', 'Time'], how='left')
    trades['LotQuantity'] = 1
    trades = trades.rename(columns={'Call/Put': 'OptionTicker'})

    return trades