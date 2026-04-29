import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import date

def analyze(symbol: str) -> dict:
    # ── DATA FETCH ────────────────────────────────────────────
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo", interval="1d")
        
        if df.empty or len(df) < 60:
            return {"error": f"Insufficient data for {symbol}. Only {len(df)} rows found."}
            
        df_h = ticker.history(period="30d", interval="1h")
        hourly_available = len(df_h) >= 48

        info = ticker.info
        stock_name    = info.get("longName") or info.get("shortName") or symbol
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or df["Close"].iloc[-1]
        sector        = info.get("sector", "N/A")
        market_cap_raw = info.get("marketCap", 0)
        market_cap    = f"{market_cap_raw/1e12:.2f}T" if market_cap_raw > 1e12 else (f"{market_cap_raw/1e9:.2f}B" if market_cap_raw else "N/A")

        close  = df["Close"]
        volume = df["Volume"]
        high   = df["High"]
        low    = df["Low"]

        # ── INDICATORS ────────────────────────────────────────────
        rsi = ta.rsi(close, length=14)
        rsi_current = rsi.iloc[-1]
        rsi_prev    = rsi.iloc[-2]
        rsi_slope   = rsi_current - rsi_prev

        price_w = close.iloc[-10:]
        rsi_w   = rsi.iloc[-10:]
        bullish_div = (close.iloc[-1] < price_w.min()) and (rsi.iloc[-1] > rsi_w.min())
        bearish_div = (close.iloc[-1] > price_w.max()) and (rsi.iloc[-1] < rsi_w.max())

        macd_df  = ta.macd(close, fast=12, slow=26, signal=9)
        macd_l   = macd_df["MACD_12_26_9"]
        sig_l    = macd_df["MACDs_12_26_9"]
        hist_l   = macd_df["MACDh_12_26_9"]
        macd_cur = macd_l.iloc[-1]; sig_cur = sig_l.iloc[-1]
        hist_cur = hist_l.iloc[-1]; hist_prv = hist_l.iloc[-2]
        macd_cross_bull = (macd_l.iloc[-2] < sig_l.iloc[-2]) and (macd_cur > sig_cur)
        macd_cross_bear = (macd_l.iloc[-2] > sig_l.iloc[-2]) and (macd_cur < sig_cur)
        hist_expand = abs(hist_cur) > abs(hist_prv)
        macd_pos    = macd_cur > 0

        bb = ta.bbands(close, length=20, std=2)
        bbl = bb.iloc[:, 0]; bbm = bb.iloc[:, 1]; bbu = bb.iloc[:, 2]
        bbw = (bbu - bbl) / bbm
        bbu_c = bbu.iloc[-1]; bbl_c = bbl.iloc[-1]; bbm_c = bbm.iloc[-1]
        bbw_c = bbw.iloc[-1]; bbw_avg = bbw.rolling(20).mean().iloc[-1]
        near_upper = current_price >= bbu_c * 0.98
        near_lower = current_price <= bbl_c * 1.02
        squeeze    = bbw_c < bbw_avg * 0.80
        squeeze_ex = bbw_c > bbw_avg and bbw.iloc[-2] < bbw_avg

        ema20 = ta.ema(close, length=20); ema50 = ta.ema(close, length=50)
        e20 = ema20.iloc[-1]; e50 = ema50.iloc[-1]
        golden = (ema20.iloc[-2] < ema50.iloc[-2]) and (e20 > e50)
        death  = (ema20.iloc[-2] > ema50.iloc[-2]) and (e20 < e50)
        above20 = current_price > e20; above50 = current_price > e50
        e20_slope = e20 - ema20.iloc[-5]
        bull_align = above20 and above50 and e20_slope > 0
        bear_align = (not above20) and (not above50) and e20_slope < 0

        vol_sma = volume.rolling(20).mean()
        vol_ratio = volume.iloc[-1] / vol_sma.iloc[-1]
        hv_bull = (vol_ratio > 1.5) and (close.iloc[-1] > close.iloc[-2])
        hv_bear = (vol_ratio > 1.5) and (close.iloc[-1] < close.iloc[-2])
        dry_up  = vol_ratio < 0.7
        lv_rally = (close.iloc[-1] > close.iloc[-2]) and dry_up

        # ── NEW INDICATORS ─────────────────────────────────────────
        stoch = ta.stoch(high, low, close)
        stoch_k = stoch.iloc[:, 0].iloc[-1] if stoch is not None else 50
        stoch_d = stoch.iloc[:, 1].iloc[-1] if stoch is not None else 50
        
        adx_df = ta.adx(high, low, close)
        adx = adx_df.iloc[:, 0].iloc[-1] if adx_df is not None and not adx_df.empty else 0
        
        atr_df = ta.atr(high, low, close)
        atr = atr_df.iloc[-1] if atr_df is not None and not atr_df.empty else 0

        # Create price history for chart (last 30 days)
        recent_df = df.tail(30)
        chart_data = [{"date": d.strftime('%Y-%m-%d'), "price": p} for d, p in zip(recent_df.index, recent_df["Close"])]

        # ── MULTI-TIMEFRAME ───────────────────────────────────────
        tf_align = "UNAVAILABLE"
        if hourly_available:
            hc = df_h["Close"]
            e20_h = ta.ema(hc, length=20); e50_h = ta.ema(hc, length=50)
            htf_bull_trend = e20_h.iloc[-1] > e50_h.iloc[-1]
            if htf_bull_trend and bull_align:   tf_align = "ALIGNED_BULL"
            elif (not htf_bull_trend) and bear_align: tf_align = "ALIGNED_BEAR"
            else: tf_align = "CONFLICTED"

        # ── SCORING ───────────────────────────────────────────────
        score = 0; signals = []
        if rsi_current < 30 and rsi_slope > 0 and not bear_align:
            score += 2; signals.append("RSI oversold + turning up (+2)")
        elif rsi_current > 70 and rsi_slope < 0 and not bull_align:
            score -= 2; signals.append("RSI overbought + turning down (-2)")
        elif 60 <= rsi_current <= 70 and bull_align:
            score += 1; signals.append("RSI strong momentum zone (+1)")
        elif 30 <= rsi_current <= 40 and bear_align:
            score -= 1; signals.append("RSI weak zone in downtrend (-1)")
        
        if bullish_div: score += 2; signals.append("RSI bullish divergence (+2)")
        if bearish_div: score -= 2; signals.append("RSI bearish divergence (-2)")

        if macd_cross_bull and macd_pos and hist_expand:
            score += 3; signals.append("MACD bullish crossover above zero + expanding (+3)")
        elif macd_cross_bull and not macd_pos:
            score += 1; signals.append("MACD bullish crossover below zero (+1)")
        elif macd_cross_bear and not macd_pos and hist_expand:
            score -= 3; signals.append("MACD bearish crossover below zero + expanding (-3)")
        elif macd_cross_bear and macd_pos:
            score -= 1; signals.append("MACD bearish crossover above zero (-1)")
        elif hist_expand and macd_pos:
            score += 1; signals.append("MACD momentum building above zero (+1)")
        elif hist_expand and not macd_pos:
            score -= 1; signals.append("MACD momentum building below zero (-1)")

        if near_lower and not squeeze and rsi_current < 40:
            score += 2; signals.append("Price at lower BB + RSI weak = reversal setup (+2)")
        elif near_upper and bull_align and hv_bull:
            score += 1; signals.append("Price walking upper BB in uptrend (+1)")
        elif near_upper and not bull_align:
            score -= 1; signals.append("Price at upper BB in non-uptrend = overextension (-1)")
        if squeeze_ex and bull_align:
            score += 1; signals.append("BB squeeze breakout upside (+1)")
        elif squeeze_ex and bear_align:
            score -= 1; signals.append("BB squeeze breakout downside (-1)")

        if golden:   score += 2; signals.append("Golden Cross EMA20 > EMA50 (+2)")
        elif death:  score -= 2; signals.append("Death Cross EMA20 < EMA50 (-2)")
        elif bull_align: score += 1; signals.append("Price above both EMAs bullish (+1)")
        elif bear_align: score -= 1; signals.append("Price below both EMAs bearish (-1)")

        if hv_bull:   score += 1; signals.append("High volume up candle (+1)")
        elif hv_bear: score -= 1; signals.append("High volume down candle (-1)")
        elif lv_rally: score -= 1; signals.append("Low volume rally — weak (+1)")

        if tf_align == "ALIGNED_BULL":   score += 2; signals.append("Daily+Hourly aligned bull (+2)")
        elif tf_align == "ALIGNED_BEAR": score -= 2; signals.append("Daily+Hourly aligned bear (-2)")

        if adx > 25 and bull_align: score += 1; signals.append("ADX > 25 (Strong Uptrend) (+1)")
        elif adx > 25 and bear_align: score -= 1; signals.append("ADX > 25 (Strong Downtrend) (-1)")
        
        if stoch_k < 20 and stoch_k > stoch_d: score += 1; signals.append("Stoch Oversold Bullish Cross (+1)")
        elif stoch_k > 80 and stoch_k < stoch_d: score -= 1; signals.append("Stoch Overbought Bearish Cross (-1)")

        score = max(-10, min(10, score))

        bull_c = sum(1 for s in signals if "(+" in s)
        bear_c = sum(1 for s in signals if "(-" in s)
        conflict_ratio = min(bull_c, bear_c) / max(bull_c + bear_c, 1)
        high_conflict = conflict_ratio > 0.4

        # ── DECISION ─────────────────────────────────────────────
        if squeeze and not squeeze_ex:
            decision = "HOLD"; override_note = "⚠️ Bollinger squeeze active — await breakout direction."
        elif score >= 4:  decision = "BUY";  override_note = ""
        elif score <= -4: decision = "SELL"; override_note = ""
        else:             decision = "HOLD"; override_note = ""

        trend = "BULLISH" if score >= 3 or bull_align else ("BEARISH" if score <= -3 or bear_align else "SIDEWAYS")

        if high_conflict or tf_align == "CONFLICTED" or (squeeze and not squeeze_ex):
            confidence = "Low"
            conf_val = 1
        elif abs(score) >= 7:
            confidence = "High"
            conf_val = 3
        elif abs(score) >= 4:
            confidence = "Medium"
            conf_val = 2
        else:
            confidence = "Low"
            conf_val = 1

        vol_state  = "SQUEEZE ACTIVE" if squeeze else ("SQUEEZE EXPANDING" if squeeze_ex else "NORMAL")
        rsi_zone   = "Oversold" if rsi_current < 30 else ("Overbought" if rsi_current > 70 else "Neutral")
        macd_state = "Bullish Cross" if macd_cross_bull else ("Bearish Cross" if macd_cross_bear else "Neutral")
        
        # Risk Notes
        risks = []
        if squeeze and not squeeze_ex: risks.append("BB squeeze pending — wait for directional breakout before entering.")
        if high_conflict: risks.append("Conflicting signals detected — consider reducing position size.")
        if bullish_div: risks.append("RSI bullish divergence present — watch for confirmation candle.")
        if bearish_div: risks.append("RSI bearish divergence present — potential reversal risk.")
        if lv_rally: risks.append("Low volume rally — institutional conviction is absent.")
        if tf_align == "CONFLICTED": risks.append("Timeframe conflict — daily and hourly trends disagree.")
        risks.append("This is a technical analysis report only. Combine with fundamental research and proper risk management before trading.")

        # Reasoning Text Generation
        reasoning = f"Momentum is {'strong' if score > 3 else 'weak' if score < -3 else 'neutral'} following recent price action. "
        reasoning += f"{symbol} is currently in a {trend.lower()} trend. "
        if squeeze: reasoning += "Volatility is contracting, indicating a potential breakout soon. "
        elif squeeze_ex: reasoning += "A volatility breakout is currently expanding. "
        reasoning += f"The MACD shows a {macd_state.lower()} signal. "
        reasoning += "Overall, the composite score suggests a " + decision + " position."

        data = {
            "stock_name": stock_name,
            "symbol": symbol.upper(),
            "sector": sector,
            "current_price": current_price,
            "market_cap": market_cap,
            "analysis_date": str(date.today()),
            "trend": trend,
            "tf_align": tf_align,
            "vol_state": vol_state,
            "metrics": [
                {"name": "RSI (14)", "value": f"{rsi_current:.1f}", "signal": rsi_zone},
                {"name": "Stochastic", "value": f"{stoch_k:.1f}", "signal": "Oversold" if stoch_k < 20 else "Overbought" if stoch_k > 80 else "Neutral"},
                {"name": "MACD", "value": f"{macd_cur:.3f}", "signal": macd_state},
                {"name": "ADX", "value": f"{adx:.1f}", "signal": "Strong Trend" if adx > 25 else "Weak Trend"},
                {"name": "ATR", "value": f"{atr:.2f}", "signal": "Volatility"},
                {"name": "EMA 20", "value": f"{e20:.2f}", "signal": "Support" if above20 else "Resistance"},
                {"name": "EMA 50", "value": f"{e50:.2f}", "signal": "Support" if above50 else "Resistance"},
                {"name": "Volume", "value": f"{vol_ratio:.2f}x avg", "signal": "Above Average" if vol_ratio > 1 else "Below Average"},
            ],
            "chart_data": chart_data,
            "scored_signals": signals,
            "score": score,
            "decision": decision,
            "confidence_level": confidence,
            "confidence_stars": conf_val,
            "reasoning": reasoning,
            "risk_notes": risks
        }
        
        # Original text format
        conf_stars = {"High": "⭐⭐⭐", "Medium": "⭐⭐", "Low": "⭐"}[confidence]
        dec_icon   = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[decision]
        bb_state   = "At Lower Band" if near_lower else ("At Upper Band" if near_upper else "Inside Bands")
        div_state  = "Bullish Divergence" if bullish_div else ("Bearish Divergence" if bearish_div else "None")
        vol_state_short = "High Volume Up" if hv_bull else ("High Volume Down" if hv_bear else ("Dry-up" if dry_up else "Normal"))

        signals_text = "\n   ".join(f"• {s}" for s in signals)

        report = f"""
╔══════════════════════════════════════════════════════════╗
║            📊  QUANTEDGE STOCK ANALYSIS REPORT           ║
╚══════════════════════════════════════════════════════════╝

1. 🏢 Stock Name        : {stock_name} ({symbol}) | Sector: {sector}
   💰 Current Price     : {current_price:.2f}
   📦 Market Cap        : {market_cap}
   📅 Analysis Date     : {date.today()}

──────────────────────────────────────────────────────────
2. 📈 Current Trend     : {trend.capitalize()}
   🔀 Timeframe Align   : {tf_align}
   📉 Volatility State  : {vol_state.title()}

──────────────────────────────────────────────────────────
3. 🔍 Signals Summary

   Indicator        | Value           | Signal
   ──────────────────────────────────────────────────────
   RSI (14)         | {rsi_current:.1f}          | {rsi_zone}
   MACD             | {macd_cur:.4f}       | {macd_state}
   Bollinger Bands  | Width: {bbw_c:.3f}   | {bb_state}
   EMA 20           | {e20:.2f}         | Price {'above ✅' if above20 else 'below ❌'}
   EMA 50           | {e50:.2f}         | Price {'above ✅' if above50 else 'below ❌'}
   Volume Ratio     | {vol_ratio:.2f}x avg       | {vol_state_short}
   RSI Divergence   | {div_state}

   📋 Scored Signals:
   {signals_text}

   ⚖️  Composite Score  : {score:+d} / 10

──────────────────────────────────────────────────────────
4. 🎯 Final Decision    : {decision} {dec_icon}
   {override_note}

5. 📊 Confidence Level  : {confidence} {conf_stars}

──────────────────────────────────────────────────────────
6. 🧠 Reasoning (Plain Language):

   {reasoning}

──────────────────────────────────────────────────────────
7. ⚠️  Risk Notes:

   {"\n   ".join("• " + r for r in risks)}

╚══════════════════════════════════════════════════════════╝
"""
        return {"report": report.strip(), "data": data}
        
    except Exception as e:
        return {"error": str(e)}
