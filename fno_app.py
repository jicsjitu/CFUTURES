import streamlit as st
import pandas as pd
import time
from fno_data import fetch_coindcx_klines
from fno_strategy import analyze_fno_trade

# 1. Setup Page Config (Full Width, No Title)
st.set_page_config(page_title="PRO F&O Terminal", layout="wide", initial_sidebar_state="collapsed")

# 2. Ultra-Clean Custom CSS (Hidden default headers, premium cards)
st.markdown("""
    <style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* App Background */
    .stApp { background-color: #09090B; color: #FAFAFA; font-family: 'Inter', sans-serif; }
    
    /* Premium Hover Cards */
    .card { 
        background-color: #121214; 
        padding: 20px 24px; 
        border-radius: 12px; 
        border: 1px solid #27272A;
        margin-bottom: 16px; 
        transition: all 0.2s ease-in-out;
    }
    .card:hover {
        border-color: #3F3F46;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* Typography */
    .label { color: #A1A1AA; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;}
    .val { font-size: 16px; font-weight: 700; margin-top: 4px; color: #FAFAFA; }
    
    /* Signal Colors */
    .green-text { color: #10B981; text-shadow: 0 0 10px rgba(16,185,129,0.2); }
    .red-text { color: #EF4444; text-shadow: 0 0 10px rgba(239,68,68,0.2); }
    .wait-text { color: #F59E0B; }
    
    /* Top Controls Row */
    .controls-container { padding-bottom: 20px; border-bottom: 1px solid #27272A; margin-bottom: 24px; }
    </style>
""", unsafe_allow_html=True)

# 3. Top Controls (Minimalist)
st.markdown('<div class="controls-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 8])
with col1:
    timeframe = st.selectbox("TIMEFRAME", ["15m", "1h", "4h"], index=1, label_visibility="collapsed")
with col2:
    st.button("🔄 SYNC DATA")
with col3:
    st.markdown("<div style='text-align: right; padding-top: 8px;'><span class='label'>F&O CAPITAL</span><br><span class='val'>$1,000 USDT</span></div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 4. F&O Pairs Array
pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "AVAX_USDT", "SUI_USDT"]

# 5. Data Fetch & UI Rendering
for pair in pairs:
    df, live_price = fetch_coindcx_klines(pair, interval=timeframe)
    
    if not df.empty:
        analysis = analyze_fno_trade(df)
        
        if "LONG" in analysis['signal']:
            sig_html = f"<span class='val green-text'>LONG 🟢</span>"
        elif "SHORT" in analysis['signal']:
            sig_html = f"<span class='val red-text'>SHORT 🔴</span>"
        else:
            sig_html = f"<span class='val wait-text'>WAIT ⚪</span>"

        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1, 2.5])
            
            with c1:
                st.markdown(f"<div class='label'>PAIR</div><div class='val'>{pair.replace('_', '/')}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='label'>PRICE</div><div class='val'>${live_price:,.4f}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='label'>SIGNAL</div><div>{sig_html}</div>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<div class='label'>SCORE</div><div class='val'>{analysis['score']}</div>", unsafe_allow_html=True)
            with c5:
                st.markdown(f"<div class='label'>LOGIC</div><div class='val' style='color:#D4D4D8; font-size:14px;'>{analysis['reason']}</div>", unsafe_allow_html=True)

            if analysis['signal'] != "WAIT ⚪":
                st.markdown(f"""
                <div style='margin-top: 16px; padding-top: 12px; border-top: 1px dashed #27272A; display: flex; justify-content: space-between; font-size: 13px;'>
                    <span><span class='label'>TARGET:</span> <strong style='color:#10B981;'>${analysis['target']}</strong></span>
                    <span><span class='label'>STOP-LOSS:</span> <strong style='color:#EF4444;'>${analysis['sl']}</strong></span>
                    <span><span class='label'>LEVERAGE:</span> <strong>{analysis['leverage']}</strong></span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
