import streamlit as st
import yfinance as yf
import pandas as pd
import re

# ページ設定
st.set_page_config(page_title="Macro Analysis App", page_icon="📈", layout="wide")

# --- 言語設定の辞書 ---
lang_dict = {
    "日本語": {
        "title": "📈 株式・指数 相関分析アプリ",
        "settings": "📊 分析設定",
        "indices": "比較する市場指数",
        "extra": "個別銘柄コード (例: 7203, 7267, 7269)",
        "timescale": "⏰ 時間軸の設定",
        "interval": "データ間隔",
        "period": "表示期間",
        "run": "分析を実行",
        "chart_title": "📊 市場相関チャート (開始時 = 100)",
        "rank_title": "🏆 騰落率ランキング (%)",
        "show_data": "最新のデータ値を表示",
        "success": "全ての分析が完了しました！",
        "error": "データが取得できませんでした。コードが正しいか確認してください。",
        "fetch": "データを取得中...",
        "periods": ["1ヶ月", "3ヶ月", "6ヶ月", "1年", "5年"],
        "intervals": ["1日足", "1週間足", "1ヶ月足"]
    },
    "English": {
        "title": "📈 Stock & Index Analysis App",
        "settings": "📊 Analysis Settings",
        "indices": "Market Indices",
        "extra": "Stock Codes (e.g. 7203, 7267)",
        "timescale": "⏰ Time Scale",
        "interval": "Interval",
        "period": "Period",
        "run": "Run Analysis",
        "chart_title": "📊 Correlation Chart (Start = 100)",
        "rank_title": "🏆 Performance Ranking (%)",
        "show_data": "Show Latest Data Values",
        "success": "Analysis Complete!",
        "error": "No data found. Please check the stock codes.",
        "fetch": "Fetching data...",
        "periods": ["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
        "intervals": ["Daily", "Weekly", "Monthly"]
    }
}

selected_lang = st.sidebar.selectbox("🌐 Language / 言語", ["日本語", "English"])
L = lang_dict[selected_lang]
st.title(L["title"])

# --- サイドバー：分析設定 ---
st.sidebar.header(L["settings"])

# 【修正】債券を削除し、主要指数のみに絞りました
market_indices = {
    "Nikkei 225 (日本)": "^N225",
    "S&P 500 (米国)": "^GSPC",
    "NASDAQ (米国)": "^IXIC",
    "TOPIX (日本)": "^TPX"
}

selected_names = st.sidebar.multiselect(L["indices"], list(market_indices.keys()), default=["Nikkei 225 (日本)"])

# 入力欄
extra_input = st.sidebar.text_input(L["extra"], "7203, 7267, 7269")

# 時間軸
st.sidebar.header(L["timescale"])
interval_map = {"1日足": "1d", "1週間足": "1wk", "1ヶ月足": "1mo", "Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
interval_label = st.sidebar.selectbox(L["interval"], L["intervals"])
period_map = {"1ヶ月": "1mo", "3ヶ月": "3mo", "6ヶ月": "6mo", "1年": "1y", "5年": "5y", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "5 Years": "5y"}
period_label = st.sidebar.selectbox(L["period"], L["periods"])

# --- 分析実行 ---
if st.button(L["run"]):
    # 銘柄リストの作成と自動補完
    tickers = [market_indices[name] for name in selected_names]
    
    if extra_input:
        codes = [c.strip() for c in extra_input.split(",")]
        for code in codes:
            if re.match(r'^\d{4}$', code): 
                tickers.append(f"{code}.T")
            else:
                tickers.append(code)
    
    with st.spinner(L["fetch"]):
        # データの取得
        try:
            raw_data = yf.download(tickers, period=period_map[period_label], interval=interval_map[interval_label])["Close"]
            
            if isinstance(raw_data, pd.DataFrame):
                data = raw_data.dropna(axis=1, how='all')
                # 表示用ラベルのクリーンアップ (^N225 -> Nikkei225, 7203.T -> 7203)
                clean_cols = []
                for c in data.columns:
                    name = c.replace(".T", "")
                    if name == "^N225": name = "Nikkei225"
                    if name == "^GSPC": name = "S&P500"
                    if name == "^IXIC": name = "NASDAQ"
                    if name == "^TPX":  name = "TOPIX"
                    clean_cols.append(name)
                data.columns = clean_cols
            else:
                data = raw_data
        except Exception as e:
            st.error(f"Error: {e}")
            data = None

    if data is None or (isinstance(data, pd.DataFrame) and data.empty):
        st.error(L["error"])
    else:
        # 1. 市場相関チャート
        st.subheader(L["chart_title"])
        data_norm = (data / data.iloc[0]) * 100
        st.line_chart(data_norm)

        # 2. 騰落率ランキング
        st.subheader(L["rank_title"])
        perf = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
        if isinstance(perf, pd.Series):
            perf = perf.sort_values(ascending=True)
            st.bar_chart(perf, horizontal=True) 
        else:
            st.metric(label="Stock", value=f"{perf:.2f}%")

        # 3. 数値データの表示
        with st.expander(L["show_data"]):
            st.dataframe(data.tail())

        st.success(L["success"])