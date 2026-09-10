import requests
import pandas as pd
import datetime

def fetch_coindcx_klines(symbol, interval="1h"):
    # CoinDCX Public API for candles (B market for USDT pairs)
    # Note: For actual Futures Private endpoints, HMAC Auth is required.
    # This uses public spot data for analysis as price action is 99% same.
    url = f"https://public.coindcx.com/market_data/candles?pair=B-{symbol}&interval={interval}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Convert to Pandas DataFrame
        df = pd.DataFrame(data)
        # CoinDCX returns data sorted from newest to oldest. We need oldest to newest for indicators.
        df = df.iloc[::-1].reset_index(drop=True)
        
        # Keep only required columns
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])
        
        return df, df['close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame(), 0
