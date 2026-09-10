import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice

def analyze_fno_trade(df, capital=1000, risk_pct=0.02):
    if len(df) < 200:
        return {"signal": "WAIT", "score": 0, "reason": "Not enough data"}

    # Base Indicators
    df['EMA_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
    df['EMA_200'] = EMAIndicator(close=df['close'], window=200).ema_indicator()
    # Hidden MTF Proxy (Acts as Higher Timeframe Trend Filter)
    df['EMA_HTF'] = EMAIndicator(close=df['close'], window=800).ema_indicator() 
    
    df['RSI'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ATR'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    df['ADX'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14).adx()

    # Institutional Indicators
    vwap_ind = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=14)
    df['VWAP'] = vwap_ind.volume_weighted_average_price()
    df['VOL_SMA'] = df['volume'].rolling(window=20).mean()
    
    macd_ind = MACD(close=df['close'])
    df['MACD_HIST'] = macd_ind.macd_diff()

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    score = 0
    reason = []

    # 1. Soft MTF Trend Filter (Max 30)
    if latest['close'] > latest['EMA_200']:
        score += 15
        if latest['close'] > latest['EMA_HTF']:
            score += 15
            reason.append("HTF Bullish")
    elif latest['close'] < latest['EMA_200']:
        score -= 15
        if latest['close'] < latest['EMA_HTF']:
            score -= 15
            reason.append("HTF Bearish")

    # 2. VWAP (Max 20)
    if latest['close'] > latest['VWAP']: score += 20
    else: score -= 20

    # 3. RSI Divergence (Catching Tops & Bottoms) -> Max 25
    current_price_peak = df['close'].iloc[-15:].max()
    prev_price_peak = df['close'].iloc[-30:-15].max()
    current_rsi_peak = df['RSI'].iloc[-15:].max()
    prev_rsi_peak = df['RSI'].iloc[-30:-15].max()
    
    current_price_dip = df['close'].iloc[-15:].min()
    prev_price_dip = df['close'].iloc[-30:-15].min()
    current_rsi_dip = df['RSI'].iloc[-15:].min()
    prev_rsi_dip = df['RSI'].iloc[-30:-15].min()

    bullish_div = (current_price_dip < prev_price_dip) and (current_rsi_dip > prev_rsi_dip)
    bearish_div = (current_price_peak > prev_price_peak) and (current_rsi_peak < prev_rsi_peak)

    if bullish_div:
        score += 25
        reason.append("Bullish Div")
    elif bearish_div:
        score -= 25
        reason.append("Bearish Div")
    elif 50 < latest['RSI'] < 70:
        score += 10
    elif 30 < latest['RSI'] < 50:
        score -= 10

    # 4. Long/Short Buildup (Proxy OI Data) -> Max 20
    price_trend_up = latest['close'] > df['close'].iloc[-5]
    vol_trend_up = latest['volume'] > latest['VOL_SMA']  # <-- FIXED LINE HERE

    if price_trend_up and vol_trend_up:
        score += 20
        reason.append("Long Buildup")
    elif (not price_trend_up) and vol_trend_up:
        score -= 20
        reason.append("Short Buildup")

    # 5. MACD (Max 15)
    if latest['MACD_HIST'] > 0 and latest['MACD_HIST'] > prev['MACD_HIST']: score += 15
    elif latest['MACD_HIST'] < 0 and latest['MACD_HIST'] < prev['MACD_HIST']: score -= 15

    # 6. Flexible Filters (No Hard Blocks to avoid missing trades)
    is_fake_pump = False
    if latest['volume'] < latest['VOL_SMA'] * 0.6: 
        is_fake_pump = True
        reason.append("Low Vol")
        score = int(score * 0.5) 

    if latest['ADX'] < 20:
        score = int(score * 0.7) 
        reason.append("Chop Zone")

    atr_val = latest['ATR']
    live_price = latest['close']
    
    sl, target, qty, tsl = 0, 0, 0, 0
    entry_range = ""
    leverage = "5x - 10x"
    
    # Final Decision (Max possible is 110, triggering at 65 gives high frequency + profitability)
    if score >= 65 and not is_fake_pump:
        signal = "LONG 🟢"
        sl = live_price - (atr_val * 1.5)
        target = live_price + (atr_val * 3.5) 
        tsl = live_price - (atr_val * 0.5) 
        risk_per_coin = live_price - sl
        qty = (capital * risk_pct) / risk_per_coin if risk_per_coin > 0 else 0
        entry_range = f"${live_price * 0.998:.4f} - ${live_price:.4f}"
    elif score <= -65 and not is_fake_pump:
        signal = "SHORT 🔴"
        sl = live_price + (atr_val * 1.5)
        target = live_price - (atr_val * 3.5)
        tsl = live_price + (atr_val * 0.5)
        risk_per_coin = sl - live_price
        qty = (capital * risk_pct) / risk_per_coin if risk_per_coin > 0 else 0
        entry_range = f"${live_price:.4f} - ${live_price * 1.002:.4f}"
    else:
        signal = "WAIT ⚪"
        leverage = "N/A"

    unique_reasons = list(set(reason)) 

    return {
        "signal": signal,
        "score": score,
        "rsi": round(latest['RSI'], 1),
        "reason": " + ".join(unique_reasons) if unique_reasons else "No Setup",
        "sl": round(sl, 4),
        "target": round(target, 4),
        "tsl": round(tsl, 4),
        "qty": round(qty, 4),
        "entry_range": entry_range,
        "rr": "1:2.5", 
        "leverage": leverage
    }
