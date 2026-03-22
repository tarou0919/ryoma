import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser  # ニュース取得用のライブラリ

# ページの設定
st.set_page_config(page_title="株式自由分析プロ + 経済ニュース", layout="wide")

# ニュース取得関数
def get_economic_news():
    # Googleニュースのビジネスカテゴリ（日本版）のRSS
    news_url = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNR3象omV3RscVpYVjBQUVpXU0FpU2F3R0FmU2dC?hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(news_url)
    return feed.entries[:5]  # 最新5件を返す

# サイドバーの設定
with st.sidebar:
    st.header("⚙️ 分析設定")
    
    # 銘柄追加エリア
    st.subheader("1. 銘柄を追加")
    new_code = st.text_input("証券コードを入力 (例: 7203, AAPL)", "").strip()
    
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T"]

    if st.button("リストに追加"):
        if new_code:
            if new_code.isdigit() and len(new_code) == 4:
                new_code += ".T"
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
                st.success(f"{new_code} 追加")
    
    selected_tickers = st.multiselect("分析対象", options=st.session_state.ticker_list, default=st.session_state.ticker_list)
    
    if st.button("リストをクリア"):
        st.session_state.ticker_list = []
        st.rerun()

    st.subheader("2. 期間を設定")
    today = datetime.date.today()
    start_date = st.date_input("開始日", today - datetime.timedelta(days=365*3))
    end_date = st.date_input("終了日", today)

    # 【新機能】経済ニュース表示エリア
    st.markdown("---")
    st.header("📰 最新経済ニュース")
    news_list = get_economic_news()
    for entry in news_list:
        st.markdown(f"**・[{entry.title}]({entry.link})**")
        st.caption(f"公開日: {entry.published[:16]}")

# メイン画面
st.title("📊 株式自由分析 ＆ 経済ニュース")

if st.button("分析を開始する", type="primary"):
    if len(selected_tickers) < 2:
        st.error("2つ以上の銘柄を選んでください。")
    else:
        with st.spinner("データ取得中..."):
            try:
                df = yf.download(selected_tickers, start=start_date, end=end_date)
                if isinstance(df.columns, pd.MultiIndex):
                    data = df['Close']
                else:
                    data = df[['Close']]

                if not data.empty:
                    data = data.ffill()
                    st.subheader("📈 株価推移（正規化比較）")
                    st.line_chart(data / data.iloc[0] * 100)
                    
                    st.subheader("🔢 相関係数")
                    st.dataframe(data.corr().style.background_gradient(cmap='RdYlGn').format("{:.2f}"))
                    st.balloons()
            except Exception as e:
                st.error(f"エラー: {e}")