import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import urllib.parse
import plotly.express as px  # 円グラフ用

# ページの設定
st.set_page_config(page_title="株式投資・資産管理プロ", layout="wide")

# ニュース取得関数
def get_historical_news(keyword, start_date, end_date):
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    return feedparser.parse(url).entries[:5]

# 詳細情報を取得する関数
def get_stock_details(tickers):
    details = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            details.append({
                "銘柄": t,
                "名称": info.get('longName', t),
                "セクター": info.get('sector', 'その他'),
                "現在値": info.get('currentPrice', info.get('regularMarketPrice', 0)),
                "配当利回り": (info.get('dividendYield', 0) or 0) * 100
            })
        except: continue
    return pd.DataFrame(details)

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定・銘柄管理")
    new_code = st.text_input("証券コード (例: 7203, 9432)", "").strip()
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T", "8058.T"]
    
    if st.button("リストに追加"):
        if new_code:
            if new_code.isdigit() and len(new_code) == 4: new_code += ".T"
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
                st.rerun()

    selected_tickers = st.multiselect("表示対象", options=st.session_state.ticker_list, default=st.session_state.ticker_list)
    
    st.subheader("期間・ニュース設定")
    today = datetime.date.today()
    start_date = st.date_input("分析開始日", today - datetime.timedelta(days=365))
    news_keyword = st.text_input("ニュースワード", "日本 経済")

# メイン画面
st.title("📊 株式総合管理システム")

tab1, tab2, tab3 = st.tabs(["📈 株価分析", "💰 ポートフォリオ管理", "📰 経済ニュース"])

# 銘柄詳細の事前取得
if selected_tickers:
    stock_df = get_stock_details(selected_tickers)

with tab1:
    if st.button("分析を実行", type="primary"):
        df = yf.download(selected_tickers, start=start_date, end=today)
        data = df['Close'] if isinstance(df.columns, pd.MultiIndex) else df[['Close']]
        if not data.empty:
            st.subheader("正規化比較（100基準）")
            st.line_chart(data / data.iloc[0] * 100)
            st.subheader("相関係数")
            st.dataframe(data.corr().style.background_gradient(cmap='RdYlGn').format("{:.2f}"))

with tab2:
    st.header("💰 資産状況とセクター配分")
    if not stock_df.empty:
        # 入力エリア
        st.subheader("保有状況の入力")
        portfolio_input = []
        col1, col2, col3 = st.columns(3)
        for i, row in stock_df.iterrows():
            with col1: qty = st.number_input(f"{row['銘柄']} 保有数", min_value=0, step=100, key=f"q_{row['銘柄']}")
            with col2: price = st.number_input(f"{row['銘柄']} 取得単価", min_value=0.0, key=f"p_{row['銘柄']}")
            current_val = qty * row['現在値']
            profit = (row['現在値'] - price) * qty if price > 0 else 0
            portfolio_input.append({"銘柄": row['銘柄'], "セクター": row['セクター'], "現在値": row['現在値'], "取得単価": price, "保有数": qty, "評価額": current_val, "損益": profit})
        
        p_df = pd.DataFrame(portfolio_input)
        
        # 損益サマリー
        total_val = p_df['評価額'].sum()
        total_profit = p_df['損益'].sum()
        c1, c2 = st.columns(2)
        c1.metric("総評価額", f"{total_val:,.0f}円")
        c2.metric("合計損益", f"{total_profit:,.0f}円", delta=f"{total_profit:,.0f}円")

        # セクター別円グラフ
        st.subheader("業種別（セクター）配分")
        if total_val > 0:
            fig = px.pie(p_df[p_df['保有数'] > 0], values='評価額', names='セクター', hole=0.4)
            st.plotly_chart(fig)
        else:
            st.info("保有数を入力するとセクター配分が表示されます。")
        
        st.dataframe(p_df.style.format({"現在値": "{:,.1f}", "取得単価": "{:,.1f}", "評価額": "{:,.0f}", "損益": "{:,.0f}"}))

with tab3:
    st.header("📰 関連ニュース")
    news = get_historical_news(news_keyword, start_date, today)
    for entry in news:
        st.markdown(f"**・[{entry.title}]({entry.link})**")
        st.caption(f"{entry.published[:16]}")