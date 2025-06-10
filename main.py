import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from binance_client import client

st.title("Crypto Live Technical Analysis")

pair = st.selectbox("Select Pair", ["BNBUSDT", "BTCUSDT", "ETHUSDT"])
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

# Candle Chart
fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
)])

# Moving Average 5 line
fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['MA5'], name="MA 5",
    line=dict(color='orange')
))

st.plotly_chart(fig)

# RSI Chart
st.line_chart(df[['RSI']])
