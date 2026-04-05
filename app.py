import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# RTL
st.markdown("""
<style>
body { direction: RTL; text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("📊 דאשבורד מתקדם - שיטת מיכה סטוקס")

# ======================
# Sidebar
# ======================
st.sidebar.header("⚙️ הגדרות")

period = st.sidebar.selectbox(
    "טווח זמן",
    ["1mo", "3mo", "6mo", "1y"],
    index=1
)

watchlist = st.sidebar.text_area(
    "📌 רשימת מניות לסריקה (מופרד בפסיקים)",
    "AAPL,TSLA,NVDA,AMD,QQQ,SPY"
)

ticker = st.text_input("🔎 ניתוח מניה:", "AAPL")

# ======================
# פונקציה לניתוח
# ======================
def analyze_stock(ticker):
    df = yf.download(ticker, period=period, interval="1d")

    if len(df) < 30:
        return None

    df["MA20"] = ta.sma(df["Close"], length=20)
    df["CCI"] = ta.cci(df["High"], df["Low"], df["Close"], length=20)
    df["Volume_MA"] = ta.sma(df["Volume"], length=20)

    bb = ta.bbands(df["Close"])
    df["BB_LOW"] = bb["BBL_20_2.0"]
    df["BB_HIGH"] = bb["BBU_20_2.0"]

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0

    # Trend
    ma_slope = df["MA20"].iloc[-1] - df["MA20"].iloc[-5]
    if latest["Close"] > latest["MA20"] and ma_slope > 0:
        score += 1

    # Candle
    if latest["Close"] > latest["Open"]:
        score += 1

    # Volume
    vol_ratio = latest["Volume"] / latest["Volume_MA"]
    if vol_ratio > 1.2:
        score += 1

    # MA
    if latest["Close"] > latest["MA20"]:
        score += 1

    # CCI
    if -100 < latest["CCI"] < 100:
        score += 1

    # Control
    if latest["Close"] > latest["Open"]:
        score += 1

    # Levels
    recent = df.tail(20)
    support = recent["Low"].min()
    resistance = recent["High"].max()

    # Breakout
    breakout = ""
    if latest["Close"] > resistance and vol_ratio > 1.2:
        breakout = "🚀"
        score += 2
    elif latest["High"] > resistance and latest["Close"] < resistance:
        breakout = "⚠️"
    elif latest["Close"] > resistance * 0.97:
        breakout = "⏳"

    # SQUEEZE
    squeeze = False
    if (df["BB_HIGH"].iloc[-1] - df["BB_LOW"].iloc[-1]) < (df["BB_HIGH"].mean() - df["BB_LOW"].mean()) * 0.5:
        squeeze = True
        score += 1

    # דירוג
    if score >= 7:
        grade = "A"
    elif score >= 5:
        grade = "B"
    else:
        grade = "C"

    return {
        "ticker": ticker,
        "score": score,
        "grade": grade,
        "price": latest["Close"],
        "support": support,
        "resistance": resistance,
        "breakout": breakout,
        "squeeze": squeeze,
        "df": df
    }

# ======================
# תצוגת מניה
# ======================
if ticker:
    result = analyze_stock(ticker)

    if result:
        df = result["df"]

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"]
        ))
        fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20"))

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 ניתוח")

        st.write(f"**מחיר:** {round(result['price'],2)}")
        st.write(f"**תמיכה:** {round(result['support'],2)}")
        st.write(f"**התנגדות:** {round(result['resistance'],2)}")

        # מצבים
        st.subheader("📈 מצבים")

        if result["breakout"] == "🚀":
            st.success("🚀 פריצה אמיתית")
        elif result["breakout"] == "⚠️":
            st.warning("⚠️ פריצת שווא")
        elif result["breakout"] == "⏳":
            st.info("⏳ מתקרב לפריצה")

        if result["squeeze"]:
            st.warning("💥 SQUEEZE – פוטנציאל תנועה חדה")

        # דירוג
        st.subheader("🏆 דירוג סטאפ")

        if result["grade"] == "A":
            st.success("🔥 A – סטאפ חזק מאוד")
        elif result["grade"] == "B":
            st.warning("⚠️ B – סטאפ בינוני")
        else:
            st.error("❌ C – סטאפ חלש")

# ======================
# 🔎 סורק מניות
# ======================
st.subheader("🔎 הזדמנויות מהירות")

tickers = [t.strip() for t in watchlist.split(",")]

opportunities = []

for t in tickers:
    res = analyze_stock(t)
    if res and res["grade"] == "A":
        opportunities.append(res)

if opportunities:
    for o in opportunities:
        st.success(f"{o['ticker']} | מחיר: {round(o['price'],2)} | דירוג: {o['grade']}")
else:
    st.write("אין כרגע סטאפים חזקים")
