import streamlit as st
import pandas as pd
import time
from fno_data import fetch_coindcx_klines
from fno_strategy import analyze_fno_trade

# 1. Setup Page Config
st.set_page_config(page_title="PRO F&O Terminal", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #0B0B0F; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    div[data-testid="column"] button {
        background-color: #1A1A24 !important; color: #00E676 !important;
        border: 1px solid #00E676 !important; border-radius: 6px; font-weight: bold; width: 100%;
    }
    div[data-testid="column"] button:hover { background-color: #00E676 !important; color: #000000 !important; }
    
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

# 3. Top Controls Row
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
pairs = [
    # Volume Kings (Layer 1 & Core - Safest for big capital)
    "BTC_USDT", "ETH_USDT", "SOL_USDT", "BNB_USDT", "XRP_USDT",
    "ADA_USDT", "AVAX_USDT", "DOT_USDT", "NEAR_USDT", "FTM_USDT",
    "ATOM_USDT", "SUI_USDT", "SEI_USDT", "APT_USDT", "INJ_USDT",
    "TRX_USDT", "LTC_USDT", "BCH_USDT",
    
    # Layer 2 & Scaling (Fast movers, great for scalping)
    "MATIC_USDT", "ARB_USDT", "OP_USDT", "STRK_USDT", "IMX_USDT", 
    "MNT_USDT", "STX_USDT",
    
    # DeFi & Oracles (Strong institutional backing)
    "LINK_USDT", "UNI_USDT", "AAVE_USDT", "CRV_USDT", "MKR_USDT",
    "LDO_USDT", "RUNE_USDT", "DYDX_USDT", "JUP_USDT",
    
    # AI & DePIN (Current market hype & crazy momentum)
    "RNDR_USDT", "FET_USDT", "TAO_USDT", "WLD_USDT", "GRT_USDT",
    "ICP_USDT", "FIL_USDT",
    
    # Gaming & Metaverse (Good for volatility breakouts)
    "GALA_USDT", "SAND_USDT", "MANA_USDT", "AXS_USDT",
    
    # Solid Altcoins (Reliable price action)
    "ALGO_USDT", "VET_USDT", "TIA_USDT", "HBAR_USDT",
    
    # Meme Coins (High Risk/High Reward - Extremely volatile)
    "DOGE_USDT", "SHIB_USDT", "PEPE_USDT", "WIF_USDT", "FLOKI_USDT", "BONK_USDT"
]

# 5. Data Fetch, Analyze & Sort Logic
analyzed_results = []

for pair in pairs:
    df, live_price = fetch_coindcx_klines(pair, interval=timeframe)
    
    if not df.empty:
        analysis = analyze_fno_trade(df)
        
        # Apply Filter
        if filter_sig != "All" and filter_sig not in analysis['signal'].replace(" 🟢", "").replace(" 🔴", "").replace(" ⚪", ""):
            continue
            
        # Determine Sorting Priority (1 = LONG, 2 = SHORT, 3 = WAIT)
        if "LONG" in analysis['signal']:
            priority = 1
        elif "SHORT" in analysis['signal']:
            priority = 2
        else:
            priority = 3
            
        analyzed_results.append({
            "pair": pair,
            "live_price": live_price,
            "analysis": analysis,
            "priority": priority,
            "score": abs(analysis['score'])
        })

# Sort list: First by priority (LONG -> SHORT -> WAIT), then by highest score
analyzed_results = sorted(analyzed_results, key=lambda x: (x['priority'], -x['score']))

# 6. UI Rendering (Sorted Cards)
for item in analyzed_results:
    pair = item['pair']
    live_price = item['live_price']
    analysis = item['analysis']
    
    is_long = "LONG" in analysis['signal']
    is_short = "SHORT" in analysis['signal']
    
    sig_class = "buy-text" if is_long else "sell-text" if is_short else "wait-text"
    icon = "🚀 BUY TREND" if is_long else "🩸 SELL TREND" if is_short else "⏳ WAIT (Sideways)"
    arrow = "↗" if is_long else "↘" if is_short else "→"

    # HTML Card Rendering
    card_html = (
        f'<div class="pro-card">'
        f'<div class="flex-row">'
        f'<div style="width: 15%;"><div class="lbl">Pair</div><div class="val {sig_class}">{pair.replace("_", "/")}</div></div>'
        f'<div style="width: 15%;"><div class="lbl">Live Price</div><div class="val">${live_price:,.4f} {arrow}</div></div>'
        f'<div style="width: 20%;"><div class="lbl">Signal</div><div class="val {sig_class}">{icon}</div></div>'
        f'<div style="width: 15%;"><div class="lbl">Score / RSI</div><div class="val">{analysis["score"]} <span style="font-size:12px; color:#8B8B9E;">({analysis["rsi"]})</span></div></div>'
        f'<div style="width: 35%;"><div class="lbl">Analysis Logic</div><div style="color:#A0A0B0; font-size:13px; font-weight:600;">{analysis["reason"]}</div></div>'
        f'</div>'
    )
    
    if is_long or is_short:
        card_html += (
            f'<div class="trade-zone">'
            f'<div><span class="lbl">ENTRY RANGE:</span> <strong style="color:#E0E0E6;">{analysis["entry_range"]}</strong></div>'
            f'<div><span class="lbl">SAFE QTY (2% Risk):</span> <strong style="color:#2196F3;">{analysis["qty"]} Coins</strong></div>'
            f'<div><span class="lbl">TARGET:</span> <strong style="color:#00E676;">${analysis["target"]}</strong></div>'
            f'<div><span class="lbl">TRAIL-SL:</span> <strong style="color:#FFB300;">${analysis["tsl"]}</strong></div>'
            f'<div><span class="lbl">STOP-LOSS:</span> <strong style="color:#FF3D00;">${analysis["sl"]}</strong></div>'
            f'<div><span class="lbl">R:R RATIO:</span> <strong style="color:#E0E0E6;">{analysis["rr"]}</strong></div>'
            f'</div>'
        )
        
    card_html += '</div>'
    st.markdown(card_html, unsafe_allow_html=True)

# 7. Auto-Refresh Logic (Timer sabse niche chalega)
if auto_refresh:
    # Sabhi cards render hone ke baad bottom par ek empty space banayenge
    bottom_timer_slot = st.empty()
    
    for seconds_left in range(180, 0, -1):
        mins, secs = divmod(seconds_left, 60)
        timeformat = f"{mins:02d}:{secs:02d}"
        
        # UI mein sabse niche timer update karega har second
        bottom_timer_slot.markdown(
            f"<div style='text-align: center; color:#FFB300; font-size:14px; font-weight:bold; padding: 20px 0;'>⏳ Next Market Scan in: {timeformat}</div>", 
            unsafe_allow_html=True
        )
        time.sleep(1)
        
    # Timer zero hote hi page refresh hoga
    st.rerun()
