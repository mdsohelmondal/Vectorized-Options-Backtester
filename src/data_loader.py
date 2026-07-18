import pandas as pd

def load_and_preprocess_data(options_path, spot_path):
    """Reads raw options and spot data, normalizes timestamps, and prepares base DataFrames."""
    data = pd.read_csv(options_path)
    spot_data = pd.read_csv(spot_path)

    # Convert the date and time columns in spot_data
    spot_data['ts'] = pd.to_datetime(spot_data['ts'], format='%Y-%m-%d %H:%M:%S')
    spot_data['Date'] = spot_data['ts'].dt.strftime('%Y-%m-%d')
    spot_data['Time'] = spot_data['ts'].dt.strftime('%H:%M') + ':59'
    spot_data = spot_data[['Date', 'Time', 'c']].rename(columns={'c': 'BankniftyClose'}).drop_duplicates(subset=['Date', 'Time'])

    return data, spot_data
