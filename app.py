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
col1.metric("対象期間の総営業日数", f"{len(df):,}日")
col2.metric("1570終値 ＜ 日経225終値 の日数", f"{len(hit):,}日")
col3.metric("該当率", f"{len(hit)/len(df)*100:.1f}%" if len(df) > 0 else "N/A")
st.divider()

st.subheader("📅 年別集計")
by_year = hit.groupby(hit.index.year).size().rename("該当日数").to_frame()
by_year.index.name = "年"
total_by_year = df.groupby(df.index.year).size().rename("総営業日数")
by_year = by_year.join(total_by_year)
by_year["該当率(%)"] = (by_year["該当日数"] / by_year["総営業日数"] * 100).round(1)
st.dataframe(by_year, use_container_width=True)
st.divider()

st.subheader(f"📋 全{len(hit):,}件リスト（1570終値 ＜ 日経225終値）")
display = hit.copy()
display.index = display.index.strftime("%Y-%m-%d")
display["差額（1570－日経）"] = (display["1570終値"] - display["N225終値"]).round(0).astype(int)
display["1570終値"] = display["1570終値"].round(0).astype(int)
display["N225終値"] = display["N225終値"].round(0).astype(int)

def color_diff(val):
    return "color: red" if val < 0 else ""

styled = display.style.map(color_diff, subset=["差額（1570－日経）"])
st.dataframe(styled, use_container_width=True)
st.divider()
st.caption("⚠️ データはyfinance経由。投資判断はご自身の責任で。")
