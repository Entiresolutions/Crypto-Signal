import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from binance_client import client

st.title("Crypto Live Technical Analysis")

# Binance se sab pairs uthao
exchange_info = client.get_exchange_info()
symbols = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']

# Ab unhe selectbox mein daal do
pair = st.selectbox("Select Pair", symbols)

interval = st.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h"])
limit = st.slider("Select Candles", 50, 500, 100)

bars = client.get_klines(symbol=pair, interval=interval, limit=limit)

df = pd.DataFrame(bars, columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'qav', 'num_trades', 'taker_base_vol',
    'taker_quote_vol', 'ignore'
])

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['close'] = df['close'].astype(float)

# Indicators
df['RSI'] = ta.rsi(df['close'])
df['MA5'] = ta.sma(df['close'], length=5)
macd = ta.macd(df['close'])
df = pd.concat([df, macd], axis=1)

# Candle Chart
fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
)])

fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['MA5'], name="MA 5",
    line=dict(color='orange')
))

st.subheader("Candlestick + MA 5")
st.plotly_chart(fig)

# RSI Chart
st.subheader("RSI")
st.line_chart(df[['RSI']])

# MACD Chart
st.subheader("MACD")

macd_fig = go.Figure()

macd_fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['MACD_12_26_9'], name="MACD",
    line=dict(color='blue')
))

macd_fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['MACDs_12_26_9'], name="Signal",
    line=dict(color='red')
))

macd_fig.add_trace(go.Bar(
    x=df['timestamp'], y=df['MACDh_12_26_9'], name="Histogram",
    marker_color='green'
))

st.plotly_chart(macd_fig)

# 📊 Automated Analysis Summary

# Get latest values
last_rsi = df['RSI'].iloc[-1]
last_macd = df['MACD_12_26_9'].iloc[-1]
last_signal = df['MACDs_12_26_9'].iloc[-1]
last_close = df['close'].iloc[-1]
last_ma5 = df['MA5'].iloc[-1]

# RSI Analysis
if last_rsi > 70:
    rsi_comment = "Market is Overbought"
elif last_rsi < 30:
    rsi_comment = "Market is Oversold"
else:
    rsi_comment = "RSI is Neutral"

# MACD Analysis
if last_macd > last_signal:
    macd_comment = "MACD indicates Bullish momentum"
elif last_macd < last_signal:
    macd_comment = "MACD indicates Bearish momentum"
else:
    macd_comment = "MACD is Neutral"

# MA5 Analysis
if last_close > last_ma5:
    ma5_comment = "Price is above MA5, indicating Uptrend"
else:
    ma5_comment = "Price is below MA5, indicating Downtrend"

# Combine Summary
summary = f"""
**Market Analysis Summary:**

- RSI: {last_rsi:.2f} → {rsi_comment}
- MACD: {last_macd:.4f}, Signal: {last_signal:.4f} → {macd_comment}
- Last Close: {last_close}, MA5: {last_ma5:.4f} → {ma5_comment}
"""

# Show the Analysis Summary
st.subheader("📊 Auto Market Summary")
st.markdown(summary)
