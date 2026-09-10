import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice

def analyze_fno_trade(df, capital=1000, risk_pct=0.02):
    if len(df) < 200:
        return {"signal": "WAIT", "score": 0, "reason": "Not enough data"}

    # 1. Base Indicators (Tumhara Purana Logic)
    df['EMA_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
    df['EMA_200'] = EMAIndicator(close=df['close'], window=200).ema_indicator()
    df['RSI'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ATR'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    
    adx_ind = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ADX'] = adx_ind.adx()

    # 2. PRO Indicators (Naya Institutional Logic)
    vwap_ind = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=14)
    df['VWAP'] = vwap_ind.volume_weighted_average_price()
    df['VOL_SMA'] = df['volume'].rolling(window=20).mean() # 20-period Avg Volume
    
    macd_ind = MACD(close=df['close'])
    df['MACD_HIST'] = macd_ind.macd_diff()

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    score = 0
    reason = []

    # A. Trend Filter (Max 30 points)
    if latest['close'] > latest['EMA_200'] and latest['EMA_50'] > latest['EMA_200']:
        score += 30
        reason.append("Bullish Trend")
    elif latest['close'] < latest['EMA_200'] and latest['EMA_50'] < latest['EMA_200']:
        score -= 30
        reason.append("Bearish Trend")

    # B. Institutional Filter VWAP (Max 20 points)
    if latest['close'] > latest['VWAP']:
        score += 20
    else:
        score -= 20

    # C. Momentum Filter RSI (Max 20 points)
    if 50 < latest['RSI'] < 70:
        score += 20
    elif 30 < latest['RSI'] < 50:
        score -= 20
    elif latest['RSI'] >= 70:
        reason.append("Overbought")
    elif latest['RSI'] <= 30:
        reason.append("Oversold")

    # D. Pin-point Entry MACD (Max 20 points)
    if latest['MACD_HIST'] > 0 and latest['MACD_HIST'] > prev['MACD_HIST']:
        score += 20
    elif latest['MACD_HIST'] < 0 and latest['MACD_HIST'] < prev['MACD_HIST']:
        score -= 20

    # E. Volume Anomaly (Fake Breakout Trap Filter)
    is_fake_pump = False
    if latest['volume'] < latest['VOL_SMA'] * 0.8:
        is_fake_pump = True
        reason.append("Low Vol (Fake Move)")
        score = int(score * 0.5) # Cut score in half if volume is dead

    # F. Trend Strength Filter (Avoid Sideways)
    if latest['ADX'] < 20:
        score = 0
        reason.append("Sideways Market")

    # Dynamic Stop Loss, Target, & Position Sizing Calculation
    atr_val = latest['ATR']
    live_price = latest['close']
    
    sl, target, qty = 0, 0, 0
    entry_range = ""
    leverage = "5x - 10x" # Safe F&O leverage
    
    # Generate Output (Stricter threshold: 70 points out of 90)
    if score >= 70 and not is_fake_pump:
        signal = "LONG 🟢"
        sl = live_price - (atr_val * 1.5)
        target = live_price + (atr_val * 3.0)
        risk_per_coin = live_price - sl
        qty = (capital * risk_pct) / risk_per_coin if risk_per_coin > 0 else 0
        entry_range = f"${live_price * 0.998:.4f} - ${live_price:.4f}"
    elif score <= -70 and not is_fake_pump:
        signal = "SHORT 🔴"
        sl = live_price + (atr_val * 1.5)
        target = live_price - (atr_val * 3.0)
        risk_per_coin = sl - live_price
        qty = (capital * risk_pct) / risk_per_coin if risk_per_coin > 0 else 0
        entry_range = f"${live_price:.4f} - ${live_price * 1.002:.4f}"
    else:
        signal = "WAIT ⚪"
        leverage = "N/A"

    return {
        "signal": signal,
        "score": score,
        "rsi": round(latest['RSI'], 1),
        "reason": " + ".join(reason) if reason else "No Clear Setup",
        "sl": round(sl, 4),
        "target": round(target, 4),
        "qty": round(qty, 4),
        "entry_range": entry_range,
        "rr": "1:2",
        "leverage": leverage
    }
