import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import pandas_ta as ta
from binance.client import Client
import os
import requests
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="Crypto Pro Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS Styling ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Variables */
    :root {
        --primary-bg: #0a0e1a;
        --secondary-bg: #1a1f2e;
        --accent-bg: #2d3548;
        --card-bg: rgba(29, 35, 52, 0.8);
        --glass-bg: rgba(255, 255, 255, 0.05);
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --danger-gradient: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --info-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --text-primary: #ffffff;
        --text-secondary: #ffffff;
        --text-muted: #ffffff;
        --border-color: rgba(255, 255, 255, 0.1);
        --shadow-light: 0 4px 20px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 8px 32px rgba(0, 0, 0, 0.2);
        --shadow-heavy: 0 16px 64px rgba(0, 0, 0, 0.3);
    }

    /* Main App Styling */
    .stApp {
        background: var(--primary-bg);
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--secondary-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent-bg);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #4a5568;
    }

    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: var(--shadow-heavy);
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }

    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* Enhanced Metric Cards */
    .metric-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-medium);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--primary-gradient);
    }

    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: var(--shadow-heavy);
        border-color: rgba(102, 126, 234, 0.5);
    }

    .metric-card h2 {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .metric-card h3 {
        color: var(--text-secondary);
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .metric-card h4 {
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .metric-card p {
        color: var(--text-muted);
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }

    /* Enhanced Buttons */
    .stButton > button {
        background: var(--primary-gradient) !important;
        border: none !important;
        color: white !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-light) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-medium) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Status Badges */
    .status-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
        margin: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: var(--shadow-light);
    }

    .bullish {
        background: var(--success-gradient);
        color: white;
    }

    .bearish {
        background: var(--danger-gradient);
        color: white;
    }

    .neutral {
        background: var(--warning-gradient);
        color: white;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: var(--secondary-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    .sidebar-content {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-light);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--secondary-bg);
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        margin: 0 0.25rem !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--accent-bg) !important;
        color: var(--text-secondary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
        box-shadow: var(--shadow-light) !important;
    }

    /* Metrics Styling */
    .css-1xarl3l {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-light) !important;
    }

    /* Select Box Styling */
    .stSelectbox > div > div {
        background: var(--accent-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* Text Input Styling */
    .stTextInput > div > div {
        background: var(--accent-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* Slider Styling */
    .stSlider > div > div > div {
        background: var(--primary-gradient) !important;
    }

    /* Loading Animation */
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Custom Info Cards */
    .info-card {
        background: var(--info-gradient);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
        font-weight: 500;
    }

    .success-card {
        background: var(--success-gradient);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
        font-weight: 500;
    }

    .warning-card {
        background: var(--warning-gradient);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
        font-weight: 500;
    }

    /* Chart Container */
    .js-plotly-plot {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-medium) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* Enhanced Footer */
    .footer {
        background: var(--secondary-bg);
        border-top: 1px solid var(--border-color);
        padding: 2rem;
        text-align: center;
        color: var(--text-muted);
        margin-top: 3rem;
        border-radius: 16px 16px 0 0;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }

        .main-header p {
            font-size: 1rem;
        }

        .metric-card {
            padding: 1.5rem;
        }
    }

    /* Custom Toggle Switch */
    .stToggle > div {
        background: var(--accent-bg) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* Enhanced Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
            /* --- UI/UX IMPROVEMENT: Custom Metric Styling --- */
.stMetric {
    background-color: transparent !important; /* Make card background shine through */
    border: none !important;
    padding: 0 !important;
    text-align: center; /* Center align the metrics */
}
.stMetric > label {
    color: var(--text-secondary) !important; /* Change the label color */
    font-weight: 500;
}
.stMetric > div[data-testid="stMetricValue"] {
    color: var(--text-primary) !important; /* Ensure value is primary white */
    font-size: 1.75rem; /* Slightly larger value text */
}
.stMetric > div[data-testid="stMetricDelta"] {
    font-size: 1rem; /* Slightly larger delta text */
}
</style>
""", unsafe_allow_html=True)

# ---------------- Binance Setup -------------------
# BUG FIX 1: Use environment variable NAMES, not their values.
# The user must create a .env file with:
# BINANCE_API_KEY="your_api_key_here"
# BINANCE_API_SECRET="your_api_secret_here"
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# IMPROVEMENT: Add a check for API keys to provide a clear error message.
if not api_key or not api_secret:
    st.error("🚨 Binance API keys not found. Please create a `.env` file with your `BINANCE_API_KEY` and `BINANCE_API_SECRET`.")
    st.info("The application cannot proceed without API keys.")
    st.stop()

client = Client(api_key, api_secret)

# ---------------- Main Header ----------------
st.markdown("""
<div class="main-header">
    <h1>🚀 CRYPTO PRO ANALYZER</h1>
    <p>Advanced Technical Analysis & AI-Powered Market Insights</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Sidebar Configuration ----------------
with st.sidebar:
    st.markdown("### 🎛️ Trading Parameters")

    # Trading pair input with popular suggestions
    st.markdown("**Select Trading Pair:**")
    popular_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "MATICUSDT"]

    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.selectbox("", popular_pairs, index=0, label_visibility="collapsed")
    with col2:
        custom_symbol = st.text_input("Custom", placeholder="e.g., LINKUSDT", label_visibility="collapsed")

    if custom_symbol:
        symbol = custom_symbol.upper()

    # Time interval selection
    st.markdown("**Time Interval:**")
    interval_options = {
        "1 Minute": "1m",
        "5 Minutes": "5m",
        "15 Minutes": "15m",
        "1 Hour": "1h",
        "4 Hours": "4h",
        "1 Day": "1d"
    }
    interval_display = st.selectbox("", list(interval_options.keys()), index=2, label_visibility="collapsed")
    interval = interval_options[interval_display]

    # Number of candles
    st.markdown("**Analysis Period:**")
    limit = st.slider("Number of Candles", 50, 1000, 200, step=50)

    # Support/Resistance window
    st.markdown("**S/R Analysis Window:**")
    window_size = st.slider("Candles for S/R", 10, 100, 30, step=5)

    # Auto-refresh option
    st.markdown("**Auto Refresh:**")
    auto_refresh = st.toggle("Enable Auto Refresh (30s)")

    if auto_refresh:
        time.sleep(30)
        st.rerun()

# ---------------- Main Content Area ----------------
# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["📈 Chart Analysis", "🌐 Multi-Source Data", "📊 Technical Summary", "🤖 AI Analysis"])

# ---------------- Data Fetching ----------------
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_binance_data(symbol, interval, limit):
    bars = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume',
                                     'close_time','qav','trades','tb_base_vol','tb_quote_vol','ignore'])

    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)

    # Calculate indicators
    df['EMA12'] = ta.ema(df['close'], 12)
    df['EMA26'] = ta.ema(df['close'], 26)
    df['RSI'] = ta.rsi(df['close'])
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(df['close']).iloc[:, 0], ta.bbands(df['close']).iloc[:, 1], ta.bbands(df['close']).iloc[:, 2]

    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)

    return df

try:
    with st.spinner("🔄 Fetching market data..."):
        df = fetch_binance_data(symbol, interval, limit)

    # Calculate key metrics
    recent_high = df['high'].tail(window_size).max()
    recent_low = df['low'].tail(window_size).min()
    last_close = df['close'].iloc[-1]
    price_change = ((last_close - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100

    # Support/Resistance levels
    pivot = (recent_high + recent_low + last_close) / 3
    R1 = (2 * pivot) - recent_low
    S1 = (2 * pivot) - recent_high
    R2 = pivot + (recent_high - recent_low)
    S2 = pivot - (recent_high - recent_low)

    # ---------------- Tab 1: Chart Analysis ----------------
    with tab1:
        # Price info header
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label=f"💰 {symbol} Price",
                value=f"${last_close:,.4f}",
                delta=f"{price_change:+.2f}%"
            )

        with col2:
            st.metric(
                label="📊 24h High",
                value=f"${df['high'].tail(24).max():,.4f}" if len(df) >= 24 else f"${recent_high:,.4f}"
            )

        with col3:
            st.metric(
                label="📉 24h Low",
                value=f"${df['low'].tail(24).min():,.4f}" if len(df) >= 24 else f"${recent_low:,.4f}"
            )

        with col4:
            st.metric(
                label="📈 Volume",
                value=f"{df['volume'].iloc[-1]:,.0f}"
            )

        # Enhanced chart
        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.6, 0.15, 0.15, 0.1],
            subplot_titles=(
                f"{symbol} Price Action with Technical Indicators",
                "RSI (Relative Strength Index)",
                "MACD",
                "Volume"
            )
        )

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ), row=1, col=1)

        # EMAs
        fig.add_trace(go.Scatter(
            x=df['time'], y=df['EMA12'],
            line=dict(color='#2196F3', width=2), name='EMA 12'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df['time'], y=df['EMA26'],
            line=dict(color='#9C27B0', width=2), name='EMA 26'
        ), row=1, col=1)

        # Bollinger Bands
        if 'BB_upper' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['time'], y=df['BB_upper'],
                line=dict(color='rgba(250,250,250,0.5)', width=1),
                name='BB Upper', showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['time'], y=df['BB_lower'],
                line=dict(color='rgba(250,250,250,0.5)', width=1),
                fill='tonexty', fillcolor='rgba(250,250,250,0.1)',
                name='BB Lower', showlegend=False
            ), row=1, col=1)

        # Support/Resistance lines
        fig.add_hline(y=R1, line_dash="dash", line_color="red",
                     annotation_text=f"R1: ${R1:.4f}", row=1, col=1)
        fig.add_hline(y=S1, line_dash="dash", line_color="green",
                     annotation_text=f"S1: ${S1:.4f}", row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(
            x=df['time'], y=df['RSI'],
            line=dict(color='#FF9800', width=2), name='RSI'
        ), row=2, col=1)

        fig.add_hline(y=70, line_color="red", line_dash="dash", row=2, col=1)
        fig.add_hline(y=50, line_color="gray", line_dash="dot", row=2, col=1)
        fig.add_hline(y=30, line_color="green", line_dash="dash", row=2, col=1)

        # MACD
        fig.add_trace(go.Scatter(
            x=df['time'], y=df['MACD_12_26_9'],
            line=dict(color='#2196F3', width=2), name='MACD'
        ), row=3, col=1)

        fig.add_trace(go.Scatter(
            x=df['time'], y=df['MACDs_12_26_9'],
            line=dict(color='#f44336', width=2), name='Signal'
        ), row=3, col=1)

        fig.add_trace(go.Bar(
            x=df['time'], y=df['MACDh_12_26_9'],
            name='Histogram',
            marker_color=['green' if x >= 0 else 'red' for x in df['MACDh_12_26_9']]
        ), row=3, col=1)

        # Volume
        colors = ['green' if close >= open else 'red'
                 for close, open in zip(df['close'], df['open'])]
        fig.add_trace(go.Bar(
            x=df['time'], y=df['volume'],
            name='Volume', marker_color=colors, opacity=0.7
        ), row=4, col=1)

        fig.update_layout(
            height=800,
            showlegend=True,
            template="plotly_dark",
            title=f"📊 {symbol} Technical Analysis Dashboard",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_multi_source_data(symbol):
        """Fetch data from multiple cryptocurrency exchanges and APIs"""

        def binance_to_coingecko_id(sym):
            mapping = {
                "BTCUSDT": "bitcoin",
                "ETHUSDT": "ethereum",
                "BNBUSDT": "binancecoin",
                "ADAUSDT": "cardano",
                "SOLUSDT": "solana",
                "DOGEUSDT": "dogecoin",
                "MATICUSDT": "matic-network",
                "LINKUSDT": "chainlink",
                "DOTUSDT": "polkadot",
                "AVAXUSDT": "avalanche-2",
                "UNIUSDT": "uniswap",
                "LTCUSDT": "litecoin",
                "BCHUSDT": "bitcoin-cash",
                "XLMUSDT": "stellar",
                "VETUSDT": "vechain",
                "TRXUSDT": "tron",
                "EOSUSDT": "eos",
                "XMRUSDT": "monero",
                "ALGOUSDT": "algorand"
            }
            return mapping.get(sym, None)

        def extract_base_symbol(trading_pair):
            """Extract base currency from trading pair (e.g., BTCUSDT -> BTC)"""
            if trading_pair.endswith('USDT'):
                return trading_pair[:-4]
            elif trading_pair.endswith('BUSD'):
                return trading_pair[:-4]
            elif trading_pair.endswith('BTC'):
                return trading_pair[:-3]
            elif trading_pair.endswith('ETH'):
                return trading_pair[:-3]
            return trading_pair[:3]  # Default fallback

        def fetch_coingecko_data(symbol):
            """Fetch data from CoinGecko API"""
            coin_id = binance_to_coingecko_id(symbol)
            if not coin_id:
                return None

            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
            try:
                response = requests.get(url, timeout=10)
                data = response.json()
                return {
                    "price": data[coin_id]["usd"],
                    "market_cap": data[coin_id].get("usd_market_cap", None),
                    "volume_24h": data[coin_id].get("usd_24h_vol", None),
                    "change_24h": data[coin_id].get("usd_24h_change", None)
                }
            except Exception as e:
                return None

        def fetch_coinmarketcap_data(symbol):
            """Fetch data from CoinMarketCap API (requires API key)"""
            cmc_api_key = os.getenv("CMC_API_KEY")
            if not cmc_api_key:
                return None

            base_symbol = extract_base_symbol(symbol)
            url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': cmc_api_key,
            }

            parameters = {
                'symbol': base_symbol,
                'convert': 'USD'
            }

            try:
                response = requests.get(url, headers=headers, params=parameters, timeout=10)
                data = response.json()

                if 'data' in data and base_symbol in data['data']:
                    coin_data = data['data'][base_symbol]['quote']['USD']
                    return {
                        "price": coin_data['price'],
                        "market_cap": coin_data.get('market_cap', None),
                        "volume_24h": coin_data.get('volume_24h', None),
                        "change_24h": coin_data.get('percent_change_24h', None)
                    }
            except Exception as e:
                return None

        def fetch_kucoin_data(symbol):
            """Fetch data from KuCoin API"""
            # Convert symbol format (BTCUSDT -> BTC-USDT)
            if symbol.endswith('USDT'):
                kucoin_symbol = symbol[:-4] + '-USDT'
            else:
                kucoin_symbol = symbol

            url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={kucoin_symbol}"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('code') == '200000' and 'data' in data:
                    price = float(data['data']['price'])
                    return {
                        "price": price,
                        "size": data['data'].get('size', None),
                        "best_ask": data['data'].get('bestAsk', None),
                        "best_bid": data['data'].get('bestBid', None)
                    }
            except Exception as e:
                return None

        def fetch_gate_data(symbol):
            """Fetch data from Gate.io API"""
            # Convert symbol format (BTCUSDT -> BTC_USDT)
            if symbol.endswith('USDT'):
                gate_symbol = symbol[:-4] + '_USDT'
            else:
                gate_symbol = symbol

            url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={gate_symbol}"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                if data and len(data) > 0:
                    ticker = data[0]
                    return {
                        "price": float(ticker['last']),
                        "volume": float(ticker.get('base_volume', 0)),
                        "change_percentage": float(ticker.get('change_percentage', 0)),
                        "high_24h": float(ticker.get('high_24h', 0)),
                        "low_24h": float(ticker.get('low_24h', 0))
                    }
            except Exception as e:
                return None

        def fetch_huobi_data(symbol):
            """Fetch data from Huobi API"""
            # Convert symbol to lowercase (BTCUSDT -> btcusdt)
            huobi_symbol = symbol.lower()

            url = f"https://api.huobi.pro/market/detail/merged?symbol={huobi_symbol}"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('status') == 'ok' and 'tick' in data:
                    tick = data['tick']
                    return {
                        "price": float(tick['close']),
                        "volume": float(tick.get('vol', 0)),
                        "high": float(tick.get('high', 0)),
                        "low": float(tick.get('low', 0)),
                        "open": float(tick.get('open', 0))
                    }
            except Exception as e:
                return None

        def fetch_okx_data(symbol):
            """Fetch data from OKX API"""
            # Convert symbol format (BTCUSDT -> BTC-USDT)
            if symbol.endswith('USDT'):
                okx_symbol = symbol[:-4] + '-USDT'
            else:
                okx_symbol = symbol

            url = f"https://www.okx.com/api/v5/market/ticker?instId={okx_symbol}"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('code') == '0' and 'data' in data and len(data['data']) > 0:
                    ticker = data['data'][0]
                    return {
                        "price": float(ticker['last']),
                        "volume": float(ticker.get('vol24h', 0)),
                        "change_24h": float(ticker.get('chg24h', 0)),
                        "high_24h": float(ticker.get('high24h', 0)),
                        "low_24h": float(ticker.get('low24h', 0))
                    }
            except Exception as e:
                return None

        def fetch_bybit_data(symbol):
            """Fetch data from Bybit API"""
            url = f"https://api.bybit.com/v2/public/tickers?symbol={symbol}"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('ret_code') == 0 and 'result' in data and len(data['result']) > 0:
                    ticker = data['result'][0]
                    return {
                        "price": float(ticker['last_price']),
                        "volume": float(ticker.get('volume_24h', 0)),
                        "change_24h": float(ticker.get('price_24h_pcnt', 0)) * 100,
                        "high_24h": float(ticker.get('high_price_24h', 0)),
                        "low_24h": float(ticker.get('low_price_24h', 0))
                    }
            except Exception as e:
                return None

        def fetch_cryptocom_data(symbol):
            """Fetch data from Crypto.com API"""
            # Convert symbol format (BTCUSDT -> BTC_USDT)
            if symbol.endswith('USDT'):
                crypto_symbol = symbol[:-4] + '_USDT'
            else:
                crypto_symbol = symbol

            url = f"https://api.crypto.com/v2/public/get-ticker?instrument_name={crypto_symbol}"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('code') == 0 and 'result' in data and 'data' in data['result']:
                    ticker = data['result']['data']
                    return {
                        "price": float(ticker['a']),
                        "volume": float(ticker.get('v', 0)),
                        "change_24h": float(ticker.get('c', 0)),
                        "high_24h": float(ticker.get('h', 0)),
                        "low_24h": float(ticker.get('l', 0))
                    }
            except Exception as e:
                return None

        # Fetch data from all sources
        sources_data = {}

        # CoinGecko (Market data)
        sources_data["coingecko"] = fetch_coingecko_data(symbol)

        # CoinMarketCap (if API key available)
        sources_data["coinmarketcap"] = fetch_coinmarketcap_data(symbol)

        # Exchange APIs
        sources_data["kucoin"] = fetch_kucoin_data(symbol)
        sources_data["gate"] = fetch_gate_data(symbol)
        sources_data["huobi"] = fetch_huobi_data(symbol)
        sources_data["okx"] = fetch_okx_data(symbol)
        sources_data["bybit"] = fetch_bybit_data(symbol)
        sources_data["cryptocom"] = fetch_cryptocom_data(symbol)

        return sources_data

    # ---------------- Tab 2: Multi-Source Data ----------------
    with tab2:
        st.subheader("🌐 Multi-Exchange Price Comparison")

        with st.spinner("🔄 Fetching multi-source data..."):
            multi_data = get_multi_source_data(symbol)

            # Create exchange comparison
            st.markdown("### 💰 Exchange Price Comparison")

            # Collect all valid price data
            exchange_data = []

            # Binance (your live data)
            exchange_data.append({
                "exchange": "Binance",
                "price": last_close,
                "status": "🟢 Live",
                "type": "exchange"
            })

            # Add other exchanges
            exchange_mapping = {
                "kucoin": "KuCoin",
                "gate": "Gate.io",
                "huobi": "Huobi",
                "okx": "OKX",
                "bybit": "Bybit",
                "cryptocom": "Crypto.com"
            }

            for key, display_name in exchange_mapping.items():
                if multi_data.get(key) and multi_data[key].get("price"):
                    price = multi_data[key]["price"]
                    diff = ((price - last_close) / last_close * 100) if last_close != 0 else 0
                    status = "🟢" if abs(diff) < 0.5 else "🟡" if abs(diff) < 2 else "🔴"

                    exchange_data.append({
                        "exchange": display_name,
                        "price": price,
                        "diff": diff,
                        "status": status,
                        "type": "exchange"
                    })

            # Display exchange prices in columns
            if len(exchange_data) > 1:
                cols = st.columns(min(4, len(exchange_data)))
                for i, data in enumerate(exchange_data[:8]):  # Show max 8 exchanges
                    col_idx = i % 4
                    with cols[col_idx]:
                        diff_text = f"Diff: {data.get('diff', 0):+.2f}%" if 'diff' in data else "Reference"
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center; padding: 1rem; margin: 0.5rem 0;">
                            <h4>{data['status']} {data['exchange']}</h4>
                            <h3>${data['price']:,.4f}</h3>
                            <p style="font-size: 0.9em; color: {'#ff4444' if data.get('diff', 0) < 0 else '#44ff44' if data.get('diff', 0) > 0 else '#888'};">
                                {diff_text}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            # Price spread analysis
            st.markdown("### 📊 Price Spread Analysis")

            prices = [data['price'] for data in exchange_data if data['type'] == 'exchange']
            if len(prices) > 1:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                spread = ((max_price - min_price) / avg_price) * 100 if avg_price != 0 else 0

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Lowest Price", f"${min_price:,.4f}")
                with col2:
                    st.metric("Highest Price", f"${max_price:,.4f}")
                with col3:
                    st.metric("Average Price", f"${avg_price:,.4f}")
                with col4:
                    st.metric("Price Spread", f"{spread:.2f}%",
                             delta=f"{'High' if spread > 1 else 'Normal'} Volatility", delta_color="inverse")

            # Market data comparison (CoinGecko vs CoinMarketCap)
            st.markdown("### 📈 Market Data Comparison")

            market_sources = []

            # CoinGecko data
            if multi_data.get("coingecko"):
                cg_data = multi_data["coingecko"]
                market_sources.append({
                    "source": "CoinGecko",
                    "price": cg_data.get("price"),
                    "market_cap": cg_data.get("market_cap"),
                    "volume_24h": cg_data.get("volume_24h"),
                    "change_24h": cg_data.get("change_24h")
                })

            # CoinMarketCap data
            if multi_data.get("coinmarketcap"):
                cmc_data = multi_data["coinmarketcap"]
                market_sources.append({
                    "source": "CoinMarketCap",
                    "price": cmc_data.get("price"),
                    "market_cap": cmc_data.get("market_cap"),
                    "volume_24h": cmc_data.get("volume_24h"),
                    "change_24h": cmc_data.get("change_24h")
                })

            if market_sources:
                cols = st.columns(len(market_sources))
                for i, source_data in enumerate(market_sources):
                    with cols[i]:
                        st.markdown(f"#### 🎯 {source_data['source']}")

                        if source_data['price'] is not None:
                            st.metric("Price", f"${source_data['price']:,.4f}")

                        if source_data['market_cap'] is not None:
                            st.metric("Market Cap", f"${source_data['market_cap']:,.0f}")

                        if source_data['volume_24h'] is not None:
                            st.metric("24h Volume", f"${source_data['volume_24h']:,.0f}")

                        if source_data['change_24h'] is not None:
                            change_color = "normal" if source_data['change_24h'] >= 0 else "inverse"
                            st.metric("24h Change", f"{source_data['change_24h']:+.2f}%",
                                    delta_color=change_color)

            # Arbitrage opportunities
            st.markdown("### ⚡ Potential Arbitrage Opportunities")

            if len(prices) > 1:
                # BUG FIX 2: Include Binance in the arbitrage calculation by sorting the full `exchange_data` list.
                sorted_exchanges = sorted(exchange_data, key=lambda x: x['price'])

                if len(sorted_exchanges) >= 2:
                    cheapest = sorted_exchanges[0]
                    most_expensive = sorted_exchanges[-1]

                    arbitrage_profit = ((most_expensive['price'] - cheapest['price']) / cheapest['price']) * 100 if cheapest['price'] !=0 else 0

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #2e8b57, #3cb371);">
                            <h4>🟢 Best Buy Opportunity</h4>
                            <h3>{cheapest['exchange']}</h3>
                            <h2>${cheapest['price']:,.4f}</h2>
                            <p>Lowest price available</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #dc143c, #ff6347);">
                            <h4>🔴 Best Sell Opportunity</h4>
                            <h3>{most_expensive['exchange']}</h3>
                            <h2>${most_expensive['price']:,.4f}</h2>
                            <p>Highest price available</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Arbitrage summary
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, #4169e1, #6495ed);">
                        <h3>💰 Potential Arbitrage Profit</h3>
                        <h2>{arbitrage_profit:.2f}%</h2>
                        <p>Buy on {cheapest['exchange']}, Sell on {most_expensive['exchange']}</p>
                        <small>⚠️ Consider fees, slippage, and transfer times</small>
                    </div>
                    """, unsafe_allow_html=True)

            # Data freshness indicator
            st.markdown("### ⏰ Data Freshness")

            current_time = datetime.now()

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🕐 Last updated: {current_time.strftime('%H:%M:%S')}")
            with col2:
                if st.button("🔄 Refresh All Data", use_container_width=True):
                    st.cache_data.clear()  # Clear cache to force refresh
                    st.rerun()

            # Exchange status summary
            st.markdown("### 📊 Exchange Availability Summary")

            available_exchanges = len([x for x in exchange_data if x['type'] == 'exchange'])
            total_attempted = len(exchange_mapping) + 1  # +1 for Binance

            success_rate = (available_exchanges / total_attempted) * 100

            status_color = "🟢" if success_rate > 80 else "🟡" if success_rate > 60 else "🔴"

            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4>{status_color} Exchange Connectivity</h4>
                <h2>{available_exchanges}/{total_attempted} Exchanges</h2>
                <p>Success Rate: {success_rate:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

            # API Keys Status
            #st.markdown("### 🔑 API Configuration Status")

            #api_status = []

            # Check CoinMarketCap API
           # if os.getenv("CMC_API_KEY"):
            
            #    st.success("✅ CoinMarketCap API: Configured")
            #else:
             #   st.warning("❌ CoinMarketCap API: Not configured (some market data may be missing)")

            # Check Gemini API
            #if os.getenv("GEMINI_API_KEY"):
             #   st.success("✅ Gemini API: Configured")
            #else:
             #   st.warning("❌ Gemini API: Not configured (AI 3.0 analysis disabled)")

            # Check OpenAI API
            #if os.getenv("OPENAI_API_KEY"):
             #   st.success("✅ OpenAI API: Configured")
            #else:
             #   st.warning("❌ OpenAI API: Not configured (AI 2.0 analysis disabled)")


            #if not os.getenv("CMC_API_KEY"):
             #   st.info("💡 **Tip**: Add CMC_API_KEY to your .env file to enable CoinMarketCap data.")

            # Add disclaimer
            st.markdown("""
            ---
            <div style="text-align: center; color: rgba(255,255,255,0.7);">
                <small>
                ⚠️ <strong>Disclaimer:</strong> Price differences may include network fees, withdrawal limits, and market liquidity variations.
                Always verify current prices on respective exchanges before trading.
                </small>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- Tab 3: Technical Summary ----------------
    with tab3:
        st.subheader("📊 Technical Analysis Summary")

        # Helper functions
        def analyze_trend(ema12, ema26):
            if ema12 > ema26:
                return "bullish", "🟢"
            elif ema12 < ema26:
                return "bearish", "🔴"
            else:
                return "neutral", "🟡"

        def analyze_rsi(rsi):
            if rsi > 70:
                return "overbought", "🔴"
            elif rsi < 30:
                return "oversold", "🟢"
            else:
                return "neutral", "🟡"

        def analyze_macd(macd_val, signal_val):
            if macd_val > signal_val:
                return "bullish crossover", "🟢"
            elif macd_val < signal_val:
                return "bearish crossover", "🔴"
            else:
                return "neutral", "🟡"

        # Calculate latest values
        ema12_latest = df['EMA12'].iloc[-1]
        ema26_latest = df['EMA26'].iloc[-1]
        rsi_latest = df['RSI'].iloc[-1]
        macd_latest = df['MACD_12_26_9'].iloc[-1]
        signal_latest = df['MACDs_12_26_9'].iloc[-1]

        # Analysis
        trend_status, trend_emoji = analyze_trend(ema12_latest, ema26_latest)
        rsi_status, rsi_emoji = analyze_rsi(rsi_latest)
        macd_status, macd_emoji = analyze_macd(macd_latest, signal_latest)

        # Display analysis
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{trend_emoji} Trend Analysis</h3>
                <h4>EMA Crossover: {trend_status.title()}</h4>
                <p>EMA12: ${ema12_latest:.4f}</p>
                <p>EMA26: ${ema26_latest:.4f}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{rsi_emoji} RSI Analysis</h3>
                <h4>Status: {rsi_status.title()}</h4>
                <p>RSI Value: {rsi_latest:.2f}</p>
                <p>Signal: {'Strong' if rsi_latest > 70 or rsi_latest < 30 else 'Moderate'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{macd_emoji} MACD Analysis</h3>
                <h4>Signal: {macd_status.title()}</h4>
                <p>MACD: {macd_latest:.6f}</p>
                <p>Signal: {signal_latest:.6f}</p>
            </div>
            """, unsafe_allow_html=True)

        # Support/Resistance levels
        st.markdown("### 📈 Key Levels")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔴 Resistance Levels</h4>
                <p><strong>R1:</strong> ${R1:.4f}</p>
                <p><strong>R2:</strong> ${R2:.4f}</p>
                <p><strong>Recent High:</strong> ${recent_high:.4f}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🟢 Support Levels</h4>
                <p><strong>S1:</strong> ${S1:.4f}</p>
                <p><strong>S2:</strong> ${S2:.4f}</p>
                <p><strong>Recent Low:</strong> ${recent_low:.4f}</p>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- Tab 4: AI Analysis ----------------
    with tab4:
        st.subheader("🤖 AI-Powered Market Insights")

        # AI setup
        openai_api_key = os.getenv("OPENAI_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)

        openai_client = None # Initialize as None
        if openai_api_key:
            openai_client = openai.OpenAI(api_key=openai_api_key)

        # Create analysis text
        analysis_text = f"""
        CRYPTO MARKET ANALYSIS FOR {symbol}

        Current Price: ${last_close:.4f}
        Price Change (last candle): {price_change:+.2f}%

        Technical Indicators ({interval_display} interval):
        - EMA12: ${ema12_latest:.4f}
        - EMA26: ${ema26_latest:.4f}
        - Trend (based on EMA crossover): {trend_status}
        - RSI (14): {rsi_latest:.2f} (Current status: {rsi_status})
        - MACD Line: {macd_latest:.6f}
        - MACD Signal Line: {signal_latest:.6f}
        - MACD Status: {macd_status}

        Key Price Levels:
        - Support S1: ${S1:.4f}
        - Support S2: ${S2:.4f}
        - Resistance R1: ${R1:.4f}
        - Resistance R2: ${R2:.4f}

        Recent Volume: {df['volume'].iloc[-1]:,.0f}
        Analysis Period: Last {limit} candles
        """

        # AI Analysis functions
        def generate_openai_analysis(summary_text):
            if not openai_client:
                return "Error: OpenAI client not initialized. Please check your API key."
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert crypto trader and technical analyst. Provide actionable trading insights based on technical analysis data. Be concise and clear. Structure your response with: 1. Overall Sentiment, 2. Key Observations, 3. Trading Strategy, and 4. Risk Management. Use markdown for formatting."},
                        {"role": "user", "content": f"Analyze this crypto market data and provide a trading plan:\n\n{summary_text}"},
                    ],
                    temperature=0.7,
                    max_tokens=600,
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"An error occurred with the OpenAI API: {str(e)}"

        def generate_gemini_analysis(summary_text):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""As a professional crypto analyst, analyze the following technical data:

                {summary_text}

                Please provide a structured analysis with these sections:
                1.  **Market Sentiment:** (e.g., Bullish, Bearish, Neutral) and a brief justification.
                2.  **Key Technical Levels:** Identify the most critical support and resistance zones to watch.
                3.  **Potential Trading Scenarios:** Outline a potential long (buy) and short (sell) scenario, including entry points, profit targets, and stop-loss levels.
                4.  **Risk Management:** Provide a crucial piece of advice for managing risk in the current market conditions.
                5.  **Short-term Outlook:** Give a brief prediction for the next few periods based on the data.

                Your analysis should be specific, actionable, and formatted cleanly using markdown."""

                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"An error occurred with the Gemini API: {str(e)}"

        # AI Analysis UI
        col1, col2 = st.columns(2)

        with col1:
            if openai_api_key:
                if st.button("🔮 AI 2.0 Analysis", key="openai_btn", use_container_width=True):
                    with st.spinner("🤖 Generating AI 2.0 analysis..."):
                        openai_result = generate_openai_analysis(analysis_text)
                        st.markdown("### 🔮 AI 2.0 Market Analysis")
                        st.markdown(f"""
                        <div class="metric-card">
                            {openai_result}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("🔑 OpenAI API key not found.")

        with col2:
            if gemini_api_key:
                if st.button("💎 AI 3.0 Analysis", key="gemini_btn", use_container_width=True):
                    with st.spinner("🤖 Generating AI Indepth analysis..."):
                        gemini_result = generate_gemini_analysis(analysis_text)
                        st.markdown("### 💎 AI 3.0 Market Analysis")
                        st.markdown(f"""
                        <div class="metric-card">
                            {gemini_result}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("🔑 Gemini API key not found.")

        # Comparative analysis
        if openai_api_key and gemini_api_key:
            st.markdown("---")
            if st.button("🚀 Generate Both AI Analyses", key="both_ai", use_container_width=True):
                with st.spinner("🤖 Generating comprehensive AI analysis from both models..."):
                    col1_both, col2_both = st.columns(2)

                    with col1_both:
                        st.markdown("### 🔮 AI 2.0 Perspective")
                        openai_result = generate_openai_analysis(analysis_text)
                        st.markdown(f"""
                        <div class="metric-card" style="height: 100%;">
                            {openai_result}
                        </div>
                        """, unsafe_allow_html=True)

                    with col2_both:
                        st.markdown("### 💎 AI 3.0 Perspective")
                        gemini_result = generate_gemini_analysis(analysis_text)
                        st.markdown(f"""
                        <div class="metric-card" style="height: 100%;">
                            {gemini_result}
                        </div>
                        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ An unexpected error occurred: {str(e)}")
    st.info("Please check the selected trading pair (e.g., 'BTCUSDT') is valid and that your internet connection is stable. If the problem persists, your API keys may have insufficient permissions.")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.7); padding: 2rem;">
    <p>🚀 Crypto Pro Analyzer | Developed By Entire Solutions | AI Powered </p>
    <p>⚠️ For educational purposes only. Not financial advice.</p>
    <p>Last updated: {} </p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
