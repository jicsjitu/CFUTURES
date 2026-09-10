import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def analyze_fno_trade(df):
    if len(df) < 200:
        return {"signal": "WAIT", "score": 0, "reason": "Not enough data"}

    # Calculate Indicators
    df['EMA_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
    df['EMA_200'] = EMAIndicator(close=df['close'], window=200).ema_indicator()
    df['RSI'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ATR'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    
    # ADX to check trend strength (Avoid chopping)
    adx_ind = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ADX'] = adx_ind.adx()

    latest = df.iloc[-1]
    
    score = 0
    reason = []

    # 1. Trend Filter (Max 40 points)
    if latest['close'] > latest['EMA_200'] and latest['EMA_50'] > latest['EMA_200']:
        score += 40
        reason.append("Bullish HTF Trend")
    elif latest['close'] < latest['EMA_200'] and latest['EMA_50'] < latest['EMA_200']:
        score -= 40
        reason.append("Bearish HTF Trend")

    # 2. Momentum Filter (Max 30 points)
    if 50 < latest['RSI'] < 70:
        score += 30 # Room to go up
    elif 30 < latest['RSI'] < 50:
        score -= 30 # Room to go down
    elif latest['RSI'] >= 70:
        reason.append("Overbought (Risky Long)")
    elif latest['RSI'] <= 30:
        reason.append("Oversold (Risky Short)")

    # 3. Trend Strength Filter (Avoid Sideways)
    if latest['ADX'] < 20:
        score = 0 # Cancel signal if sideways
        reason.append("Sideways Market (Low ADX)")

    # Dynamic Stop Loss & Target Calculation based on Volatility (ATR)
    atr_val = latest['ATR']
    live_price = latest['close']
    
    # Generate Output
    if score >= 65:
        signal = "LONG 🟢"
        sl = live_price - (atr_val * 1.5) # Pro SL logic
        target = live_price + (atr_val * 3.0) # 1:2 Risk Reward
        leverage = "5x - 10x" # Safe F&O leverage
    elif score <= -65:
        signal = "SHORT 🔴"
        sl = live_price + (atr_val * 1.5)
        target = live_price - (atr_val * 3.0)
        leverage = "5x - 10x"
    else:
        signal = "WAIT ⚪"
        sl, target = 0, 0
        leverage = "N/A"

    return {
        "signal": signal,
        "score": score,
        "rsi": round(latest['RSI'], 1),
        "reason": " + ".join(reason) if reason else "No Clear Setup",
        "sl": round(sl, 4),
        "target": round(target, 4),
        "leverage": leverage
    }
