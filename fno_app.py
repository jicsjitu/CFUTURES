import streamlit as st
import pandas as pd
import time
from fno_data import fetch_coindcx_klines
from fno_strategy import analyze_fno_trade

# 1. Setup Page Config
st.set_page_config(page_title="PRO F&O Terminal", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS for exact matching UI & PRO HTML Cards
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #0B0B0F; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Fixed Scan Button */
    div[data-testid="column"] button {
        background-color: #1A1A24 !important; color: #00E676 !important;
        border: 1px solid #00E676 !important; border-radius: 6px; font-weight: bold; width: 100%;
    }
    div[data-testid="column"] button:hover { background-color: #00E676 !important; color: #000000 !important; }
    
    /* Clean HTML Cards (No Empty Bars) */
    .pro-card {
        background: #14141C; border: 1px solid #282836; border-radius: 12px;
        padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .flex-row { display: flex; justify-content: space-between; align-items: center; }
    .lbl { font-size: 11px; color: #8B8B9E; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
    .val { font-size: 16px; font-weight: 700; color: #E0E0E6; }
    
    .buy-text { color: #00E676; text-shadow: 0 0 8px rgba(0,230,118,0.3); font-weight: bold;}
    .sell-text { color: #FF3D00; text-shadow: 0 0 8px rgba(255,61,0,0.3); font-weight: bold;}
    .wait-text { color: #FFB300; font-weight: bold;}
    
    .trade-zone {
        margin-top: 16px; padding-top: 16px; border-top: 1px dashed #282836;
        display: flex; justify-content: space-between; font-size: 13px;
        background-color: #0A0A0E; padding: 12px; border-radius: 8px;
    }
    
    .btc-banner {
        background: rgba(0, 230, 118, 0.05); border: 1px solid #00E676; color: #00E676;
        padding: 12px 20px; border-radius: 8px; font-weight: bold; margin-bottom: 24px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .btc-bearish { background: rgba(255, 61, 0, 0.05); border-color: #FF3D00; color: #FF3D00; }
    </style>
""", unsafe_allow_html=True)

# 3. Top Controls Row (Matching Old UI framework but with new styling)
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 2, 2, 2])
with c1:
    timeframe = st.selectbox("⌚ TIMEFRAME", ["15m", "1h", "4h"], index=1)
with c2:
    filter_sig = st.selectbox("🔍 FILTER SIGNAL", ["All", "LONG", "SHORT", "WAIT"])
with c3:
    st.write("")
    st.write("")
    auto_refresh = st.checkbox("☑ Auto-Refresh (3 Min)", value=True)
with c4:
    st.write("")
    st.write("")
    if st.button("⚡ SCAN MARKET"):
        st.rerun()
with c5:
    st.markdown("<div style='text-align: right; padding-top: 15px;'><span style='color:#8E8E93; font-size:12px; font-weight:bold;'>CAPITAL REQ:</span> <br><b style='font-size:16px;'>$1,000 USDT</b></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #2d2d3d; margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# Global BTC Trend Banner
btc_df, btc_price = fetch_coindcx_klines("BTC_USDT", interval="4h")
btc_trend = "BULLISH 🟢 (Altcoins Safe for Long)"
btc_class = ""
if not btc_df.empty:
    btc_analysis = analyze_fno_trade(btc_df)
    if "SHORT" in btc_analysis['signal'] or btc_analysis['score'] < 0:
        btc_trend = "BEARISH 🔴 (High Risk for Longs)"
        btc_class = "btc-bearish"
st.markdown(f"<div class='btc-banner {btc_class}'><span>👑 GLOBAL BTC (4H) TREND:</span> <span>{btc_trend}</span></div>", unsafe_allow_html=True)

# 4. F&O Pairs Array
pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "AVAX_USDT", "SUI_USDT"]

# 5. Data Fetch & UI Rendering
for pair in pairs:
    df, live_price = fetch_coindcx_klines(pair, interval=timeframe)
    
    if not df.empty:
        analysis = analyze_fno_trade(df)
        
        # Apply Filter
        if filter_sig != "All" and filter_sig not in analysis['signal'].replace(" 🟢", "").replace(" 🔴", "").replace(" ⚪", ""):
            continue
        
        is_long = "LONG" in analysis['signal']
        is_short = "SHORT" in analysis['signal']
        
        sig_class = "buy-text" if is_long else "sell-text" if is_short else "wait-text"
        icon = "🚀 BUY TREND" if is_long else "🩸 SELL TREND" if is_short else "⏳ WAIT (Sideways)"
        arrow = "↗" if is_long else "↘" if is_short else "→"

        # Pure HTML Card Layout
        card_html = f"""
        <div class="pro-card">
            <div class="flex-row">
                <div style="width: 15%;"><div class="lbl">Pair</div><div class="val {sig_class}">{pair.replace('_', '/')}</div></div>
                <div style="width: 15%;"><div class="lbl">Live Price</div><div class="val">${live_price:,.4f} {arrow}</div></div>
                <div style="width: 20%;"><div class="lbl">Signal</div><div class="val {sig_class}">{icon}</div></div>
                <div style="width: 15%;"><div class="lbl">Score / RSI</div><div class="val">{analysis['score']} <span style="font-size:12px; color:#8B8B9E;">({analysis['rsi']})</span></div></div>
                <div style="width: 35%;"><div class="lbl">Analysis Logic</div><div style="color:#A0A0B0; font-size:13px; font-weight:600;">{analysis['reason']}</div></div>
            </div>
        """
        
        if is_long or is_short:
            card_html += f"""
            <div class="trade-zone">
                <div><span class="lbl">ENTRY RANGE:</span> <strong style="color:#E0E0E6;">{analysis['entry_range']}</strong></div>
                <div><span class="lbl">SAFE QTY (2% Risk):</span> <strong style="color:#2196F3;">{analysis['qty']} Coins</strong></div>
                <div><span class="lbl">TARGET:</span> <strong style="color:#00E676;">${analysis['target']}</strong></div>
                <div><span class="lbl">STOP-LOSS:</span> <strong style="color:#FF3D00;">${analysis['sl']}</strong></div>
                <div><span class="lbl">R:R RATIO:</span> <strong style="color:#E0E0E6;">{analysis['rr']}</strong></div>
            </div>
            """
            
        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)

# 6. Auto-Refresh Logic (Runs at the very end of the script)
if auto_refresh:
    time.sleep(180) # 180 seconds = 3 minutes
    st.rerun()
