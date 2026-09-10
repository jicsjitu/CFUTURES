import streamlit as st
import pandas as pd
import time
from fno_data import fetch_coindcx_klines
from fno_strategy import analyze_fno_trade

# 1. Setup Page Config
st.set_page_config(page_title="PRO F&O Terminal", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS for exact matching UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #121212; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    .card { 
        background-color: #1a1a24; 
        padding: 16px 20px; 
        border-radius: 10px; 
        border: 1px solid #2d2d3d;
        margin-bottom: 12px; 
    }
    .label { color: #8E8E93; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; display: block;}
    .val { font-size: 15px; font-weight: bold; color: #FFFFFF;}
    
    /* Dynamic Pair Colors */
    .pair-long { color: #00E676; font-size: 18px; font-weight: 900; text-shadow: 0 0 8px rgba(0,230,118,0.3);}
    .pair-short { color: #FF3D00; font-size: 18px; font-weight: 900; text-shadow: 0 0 8px rgba(255,61,0,0.3);}
    .pair-wait { color: #FFC107; font-size: 18px; font-weight: 900; }
    
    /* Signal Text Colors */
    .sig-long { color: #00E676; font-weight: bold; }
    .sig-short { color: #FF3D00; font-weight: bold; }
    .sig-wait { color: #FFC107; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Top Controls Row (Matching Old UI)
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 2, 2, 2])
with c1:
    timeframe = st.selectbox("⌚ Timeframe", ["15m", "1h", "4h"], index=1)
with c2:
    filter_sig = st.selectbox("🔍 Filter Signal", ["All", "LONG", "SHORT", "WAIT"])
with c3:
    st.write("")
    st.write("")
    auto_refresh = st.checkbox("☑ Auto-Refresh (3 Min)", value=True)
with c4:
    st.write("")
    st.write("")
    if st.button("⚡ Scan Market"):
        st.rerun()
with c5:
    st.markdown("<div style='text-align: right; padding-top: 15px;'><span style='color:#8E8E93;'>CAPITAL REQ:</span> <b>$1,000 USDT</b></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #2d2d3d; margin-top: 0px;'>", unsafe_allow_html=True)

# 4. F&O Pairs Array
pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "AVAX_USDT", "SUI_USDT"]

# 5. Data Fetch & UI Rendering
for pair in pairs:
    df, live_price = fetch_coindcx_klines(pair, interval=timeframe)
    
    if not df.empty:
        analysis = analyze_fno_trade(df)
        
        # Apply Filter
        if filter_sig != "All" and filter_sig not in analysis['signal']:
            continue
        
        # Color Formatting logic
        if "LONG" in analysis['signal']:
            pair_class = "pair-long"
            sig_class = "sig-long"
            icon = "🚀 BUY TREND 🚀"
        elif "SHORT" in analysis['signal']:
            pair_class = "pair-short"
            sig_class = "sig-short"
            icon = "🩸 SELL TREND 🩸"
        else:
            pair_class = "pair-wait"
            sig_class = "sig-wait"
            icon = "⏳ WAIT ⏳"

        # Card HTML
        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            
            cols = st.columns([1.5, 1.5, 1.5, 1, 2.5])
            
            with cols[0]:
                st.markdown(f"<span class='label'>PAIR (Perpetual)</span><span class='{pair_class}'>{pair.replace('_', '/')}</span>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<span class='label'>LIVE PRICE</span><span class='val'>${live_price:,.4f}</span>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<span class='label'>SIGNAL</span><span class='{sig_class}'>{icon}</span>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"<span class='label'>SCORE / RSI</span><span class='val'>{analysis['score']}</span> <span style='color:#8E8E93; font-size:12px;'>({analysis['rsi']})</span>", unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f"<span class='label'>ANALYSIS REASON</span><span style='color:#B0BEC5; font-size:14px;'>{analysis['reason']}</span>", unsafe_allow_html=True)

            # Target & Stop-Loss Row (Only for active trades)
            if "WAIT" not in analysis['signal']:
                st.markdown(f"""
                <div style='margin-top: 12px; padding-top: 10px; display: flex; justify-content: space-between; font-size: 13px;'>
                    <span><span style='color: #8E8E93;'>TARGET:</span> <strong style='color:#00E676;'>${analysis['target']}</strong></span>
                    <span><span style='color: #8E8E93;'>STOP-LOSS (ATR):</span> <strong style='color:#FF3D00;'>${analysis['sl']}</strong></span>
                    <span><span style='color: #8E8E93;'>LEVERAGE:</span> <strong style='color:#2196F3;'>{analysis['leverage']}</strong></span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)

# 6. Auto-Refresh Logic (Runs at the very end of the script)
if auto_refresh:
    time.sleep(180) # 180 seconds = 3 minutes
    st.rerun()
