import requests
import pandas as pd
import datetime
import hmac
import hashlib
import json
import time
import streamlit as st

# Securely fetching keys (Using try-except so public data doesn't crash if keys are missing)
try:
    API_KEY = st.secrets["COINDCX_API_KEY"]
    SECRET_KEY = st.secrets["COINDCX_SECRET_KEY"]
except KeyError:
    API_KEY = ""
    SECRET_KEY = ""

def fetch_coindcx_klines(symbol, interval="1h"):
    # CoinDCX Public API for candles (B market for USDT pairs)
    url = f"https://public.coindcx.com/market_data/candles?pair=B-{symbol}&interval={interval}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Convert to Pandas DataFrame
        df = pd.DataFrame(data)
        
        # CoinDCX returns data sorted from newest to oldest. Reverse it for indicators.
        if not df.empty:
            df = df.iloc[::-1].reset_index(drop=True)
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            return df, df['close'].iloc[-1]
        else:
            return pd.DataFrame(), 0
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame(), 0

def create_signature(payload_str):
    secret_bytes = bytes(SECRET_KEY, 'utf-8')
    signature = hmac.new(secret_bytes, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def get_fno_positions():
    # Only run if keys exist
    if not API_KEY or not SECRET_KEY:
        return []
        
    # CoinDCX Derivatives endpoint for active positions
    url = "https://api.coindcx.com/exchange/v1/derivatives/positions" 
    
    timestamp = int(round(time.time() * 1000))
    payload = {
        "timestamp": timestamp
    }
    
    payload_str = json.dumps(payload, separators=(',', ':'))
    
    headers = {
        'X-AUTH-APIKEY': API_KEY,
        'X-AUTH-SIGNATURE': create_signature(payload_str),
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, data=payload_str, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []
