#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import yfinance as yf

# Downloading Stock Data
data = yf.download("TCS.NS", start="2026-02-01", end="2026-03-25", interval="15m", multi_level_index=False)

data.index = pd.to_datetime(data.index)
data['Date'] = data.index.date

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(1)

# Creating Features
window = 20
data['mean'] = data['Close'].rolling(window).mean()
data['std'] = data['Close'].rolling(window).std()
data['z_score'] = (data['Close'] - data['mean']) / data['std']

# Remove missing values
data.dropna(inplace=True)

# Signals
data['signal'] = 0
data.loc[data['z_score'] < -0.75, 'signal'] = 1   # BUY
data.loc[data['z_score'] > 0.75, 'signal'] = -1  # SELL


# 🔥 BACKTESTING STARTS HERE
initial_capital = 10000
capital = initial_capital
position = 0
entry_price = 0

trades = []
portfolio_values = []

for i in range(len(data)):
    price = data['Close'].iloc[i]
    signal = data['signal'].iloc[i]

    # BUY
    if signal == 1 and position == 0:
        position = capital / price
        entry_price = price
        capital = 0

    # SELL
    elif signal == -1 and position > 0:
        capital = position * price
        profit = capital - (position * entry_price)
        trades.append(profit)
        position = 0

    # Track portfolio value
    total_value = capital + (position * price)
    portfolio_values.append(total_value)

# Final exit if still holding
if position > 0:
    final_price = data['Close'].iloc[-1]
    capital = position * final_price
    profit = capital - (position * entry_price)
    trades.append(profit)
    position = 0

# Store portfolio values
data['Portfolio_Value'] = portfolio_values


# 📊 PERFORMANCE METRICS
total_return = ((capital - initial_capital) / initial_capital) * 100

wins = [t for t in trades if t > 0]
win_rate = (len(wins) / len(trades)) * 100 if trades else 0

avg_profit = np.mean(trades) if trades else 0


# 📢 RESULTS
print("\nFinal Capital:", capital)
print("Total Return (%):", total_return)
print("Number of Trades:", len(trades))
print("Win Rate (%):", win_rate)
print("Average Profit per Trade:", avg_profit)


# In[ ]:




