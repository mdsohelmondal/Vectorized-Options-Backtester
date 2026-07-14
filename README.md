# Vectorized-Options-Backtester

## Overview
This repository features a production-grade, fully vectorized quantitative backtesting framework built in Python. The engine is engineered to evaluate an intraday **Short Strangle** options trading strategy utilizing high-frequency 1-minute data for the Banknifty index and its corresponding option chain. 

To simulate realistic institutional conditions, the architecture avoids iterative row-by-row loops, relying instead on vectorized matrix operations. This ensures that data processing, strike optimization, signal generation, and statistical reporting across a full year of granular data execute in under 60 seconds.

---

## Strategy & System Mechanics

### 1. Dynamic Strike Selection Module
* **Targeting Window:** Exactly at 09:20 AM daily, the system analyzes the available option chain.
* **Selection Logic:** The module dynamically identifies and shorts one Call Option (CE) and one Put Option (PE) whose 1-minute closing prices are closest to a target premium of Rs. 50.

### 2. Signal Generation & Execution Module
* **Execution Timeline:** Positions are entered at the 09:20 AM 1-minute close price and systematically liquidated at the 15:20 PM 1-minute close price.
* **Intraday Risk Controls:** A strict 50% hard stop-loss is placed on the entry premium of each individual leg. The engine scans high-frequency "High" column data continuously to accurately flag stop-loss breach violations.

### 3. Position Sizing & Calendar Module
* **Risk Allocation:** Modeled with a fixed allocation of exactly 1 lot (lot size of 15) per day with no capital compounding.
* **Calendar Boundaries:** The framework restricts trading strictly to Week 1 data while programmatically treating Wednesday as the contract expiry day.

---

## Performance & Analytical Outputs

The engine generates a structured analytical suite across three core layers:

### 1. Detailed Trade Sheet
Compiles comprehensive granular execution metadata for every trade, including:
* Execution Timestamps (Entry/Exit Dates and Times).
* Option Ticker strings, Strike Prices, and Option Types (CE/PE).
* Entry/Exit Prices and localized transaction values (Price × Quantity).
* Gross P&L, running Cumulative P&L, daily Available Capital, and the underlying Banknifty spot closing price.

### 2. Statistical Analysis Matrix
Calculates essential portfolio risk and return metrics:
* **CAGR** (Compound Annual Growth Rate) and **Maximum Drawdown** tracking.
* **Win/Loss Distributions:** Total count and percentage of winning vs. losing trades categorized by CE, PE, and combined portfolios.
* **Regime Performance:** Average % P&L for CE and PE legs isolated across Expiry Days vs. Non-Expiry Days.

### 3. Visual Portfolio Modeling
* **Trade-Wise Equity Curve:** Plots portfolio trajectory over time derived from a base NAV of 100.
* **Drawdown Visualizations:** A continuous time-series chart mapping capital drawdowns relative to historical equity peaks.
* **Monthly Returns Matrix:** A structured table tracking percentage performance shifts computed from month-on-month ending NAV figures.

---

## Data Placement & Proprietary Data Notice (Required)

Because historical tick and high-frequency minute-level options data is proprietary and subject to strict commercial licensing, **no raw market datasets are hosted within this public repository**. 

To run the backtesting suite locally on your computer, you must configure a local data environment:
1. Create a directory named `data/` in the root folder of your local project directory.
2. Place your local market data CSV files directly inside it, ensuring they perfectly match the exact filenames expected by the ingestion module:
   * `data/Options_data_2023.csv` — The 1-minute interval historical options chain data.
   * `data/BANKNIFTY_SPOT.csv` — The historical underlying index spot data.


## Repository Structure
```text
├── data/                  # Local historical data directory (Git-ignored)
├── outputs/               # Generated Trade Sheets, Statistics, and Performance Charts
├── src/
│   ├── __init__.py
│   ├── data_loader.py     # Vectorized data parsing and chain alignment
│   ├── backtester.py      # Core execution, strike selection, and stop-loss engine
│   └── analytics.py       # Risk matrices, NAV tracking, and plotting functions
├── main.py                # Pipeline execution entry point
├── requirements.txt       # Environment dependencies
├── LICENSE
└── README.md
