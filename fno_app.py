import streamlit as st
import pandas as pd
import time
from fno_data import fetch_coindcx_klines
from fno_strategy import analyze_fno_trade

# 1. Setup Page Config (Dark Theme & Full Width)
st.set_page_config(page_title="PRO F&O Terminal", layout="wide", page_icon="⚡")

# Custom CSS for Dark Theme & Styling matching your screenshot
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .card { background-color: #1E1E2E; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .green-text { color: #00E676; font-weight: bold; }
    .red-text { color: #FF3D00; font-weight: bold; }
    .wait-text { color: #FFC107; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ PRO F&O Trading Agent")

# Controls Section
col1, col2, col3 = st.columns([2, 2, 4])
with col1:
    timeframe = st.selectbox("Timeframe", ["15m", "1h", "4h"], index=1)
with col2:
    st.write(" ")
    st.button("🔄 Refresh Data")
with col3:
    st.markdown("<h4 style='text-align: right;'>Total Capital: $1,000 USDT</h4>", unsafe_allow_html=True)

st.markdown("---")

# F&O Pairs to Track
pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "AVAX_USDT", "SUI_USDT"]

# Logic to fetch and display data
for pair in pairs:
    df, live_price = fetch_coindcx_klines(pair, interval=timeframe)
    
    if not df.empty:
        analysis = analyze_fno_trade(df)
        
        # Color coding for Signal
        if "LONG" in analysis['signal']:
            sig_html = f"<span class='green-text'>🚀 {analysis['signal']}</span>"
        elif "SHORT" in analysis['signal']:
            sig_html = f"<span class='red-text'>🩸 {analysis['signal']}</span>"
        else:
            sig_html = f"<span class='wait-text'>⏳ {analysis['signal']}</span>"

        # Create UI Card for each pair
        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1, 2.5])
            
            with c1:
                st.markdown(f"<span style='color: #8E8E93;'>PAIR (Perpetual)</span><br><b>{pair.replace('_', '/')}</b>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span style='color: #8E8E93;'>LIVE PRICE</span><br><b>${live_price:,.4f}</b>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span style='color: #8E8E93;'>SIGNAL</span><br>{sig_html}", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<span style='color: #8E8E93;'>SCORE / RSI</span><br><b>{analysis['score']}</b> / {analysis['rsi']}", unsafe_allow_html=True)
            with c5:
                st.markdown(f"<span style='color: #8E8E93;'>ANALYSIS REASON</span><br><span style='color:#B0BEC5;'>{analysis['reason']}</span>", unsafe_allow_html=True)

            # Show targets and SL only if there is a trade setup
            if analysis['signal'] != "WAIT ⚪":
                st.markdown(f"""
                <div style='margin-top: 10px; padding-top: 10px; border-top: 1px solid #333; display: flex; justify-content: space-between;'>
                    <span><span style='color: #00E676;'>TARGET:</span> ${analysis['target']}</span>
                    <span><span style='color: #FF3D00;'>STOP-LOSS (ATR):</span> ${analysis['sl']}</span>
                    <span><span style='color: #2196F3;'>RECOMMENDED LEVERAGE:</span> {analysis['leverage']}</span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)

st.caption("Risk Warning: F&O trading carries high risk. This agent uses technical probabilities, not financial advice.")
