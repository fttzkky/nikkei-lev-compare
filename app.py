import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="1570 vs 日経225 終値比較", layout="wide")
st.title("📊 1570終値 ＜ 日経225終値 の日を調べる")
st.caption("2012年以降、1570（日経レバレッジETF）の終値が日経225終値を下回った日の全記録")

@st.cache_data(ttl=3600, show_spinner="データ取得中...")
def get_data():
    start = "2012-01-01"

    n225_raw = yf.Ticker("^N225").history(start=start)
    n225_raw.index = n225_raw.index.tz_localize(None)
    n225 = n225_raw[["Close"]].copy()
    n225.columns = ["N225終値"]

    lev_raw = yf.download("1570.T", start=start, progress=False, auto_adjust=False)
    if isinstance(lev_raw.columns, pd.MultiIndex):
        lev_raw.columns = lev_raw.columns.droplevel(1)
    lev = lev_raw[["Close"]].copy()
    lev.columns = ["1570終値"]
    lev.index = pd.to_datetime(lev.index).tz_localize(None)

    df = n225.join(lev, how="inner")
    df = df.dropna()
    return df

df = get_data()

hit = df[df["1570終値"] < df["N225終値"]].copy()
hit = hit.sort_index(ascending=False)
hit.index.name = "日付"

st.subheader("📌 集計結果")
col1, col2, col3 = st.columns(3)
