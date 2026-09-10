import hmac
import hashlib
import json
import time
import requests
import pandas as pd
import streamlit as st

# Streamlit secrets se securely keys fetch karna
API_KEY = st.secrets["COINDCX_API_KEY"]
SECRET_KEY = st.secrets["COINDCX_SECRET_KEY"]

def create_signature(payload_str):
    secret_bytes = bytes(SECRET_KEY, 'utf-8')
    signature = hmac.new(secret_bytes, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def get_fno_positions():
    # CoinDCX Derivatives endpoint for active positions
    url = "https://api.coindcx.com/exchange/v1/derivatives/positions" 
    
    timestamp = int(round(time.time() * 1000))
    payload = {
        "timestamp": timestamp
    }
    
    # Payload must be a tightly packed JSON string without spaces
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
