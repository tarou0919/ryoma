import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import urllib.parse
import plotly.express as px

# ページの設定
st.set_page_config(page_title="株式投資・資産管理プロ", layout="wide")

# ニュース取得関数
def get_historical_news(keyword, start_date, end_date):
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    return feedparser.parse(url).entries[:5]

# 銘柄詳細をキャッシュして高速化
@st.cache_data(ttl=3600)
def get_stock_details(tickers):
    if not tickers:
        return pd.DataFrame()
    details = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            details.append({
                "銘柄": t,
                "名称": info.get('shortName', t),
                "セクター": info.get('sector', 'その他'),
                "現在値": info.get('currentPrice', info.get('regularMarketPrice', 0))
            })
        except: continue
    return pd.DataFrame(details)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定・銘柄管理")
    
    new_code = st.text_input("証券コード追加 (例: 7203)", "").strip()
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T", "8058.T", "1662.T"]
    
    if st.button("追加"):
        if new_code:
            if new_code.isdigit() and len(new_code) == 4: new_code += ".T"
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
                st.rerun()

    selected_tickers = st.multiselect("表示対象", options=st.session_state.ticker_list, default=st.session_state.ticker_list)
    
    # サイドバーでの保有状況入力
    st.markdown("---")
    st.subheader("💰 保有状況の入力")
    portfolio_inputs = {}
    
    # 銘柄情報の取得
    stock_df = get_stock_details(selected_tickers)
    
    if not stock_df.empty:
        for _, row in stock_df.iterrows():
            with st.expander(f"{row['名称']} ({row['銘柄']})", expanded=False):
                qty = st.number_input("保有数", min_value=0, step=10, key=f"sidebar_q_{row['銘柄']}")
                price = st.number_input("取得単価", min_value=0.0, step=1.0, key=f"sidebar_p_{row['銘柄']}")
                portfolio_inputs[row['銘柄']] = {"qty": qty, "price": price}

    st.markdown("---")
    st.subheader("分析・ニュース設定")
    start_date = st.date_input("分析開始日", datetime.date.today() - datetime.timedelta(days=365))
    news_keyword = st.text_input("ニュースワード", "日本 経済")

    st.markdown("---")
    st.subheader("📰 最新経済ニュース")
    news_entries = get_historical_news(news_keyword, start_date, datetime.date.today())
    for entry in news_entries:
        st.markdown(f"**・[{entry.title}]({entry.link})**")

# --- メイン画面 ---
st.title("📊 株式総合管理システム")

tab1, tab2 = st.tabs(["📈 株価分析", "💰 ポートフォリオ詳細"])

with tab1:
    if st.button("分析を実行", type="primary"):
        if selected_tickers:
            with st.spinner("チャート作成中..."):
                df = yf.download(selected_tickers, start=start_date, end=datetime.date.today())
                if not df.empty and 'Close' in df:
                    data = df['Close']
                    st.subheader("正規化比較（100基準）")
                    st.line_chart(data / data.iloc[0] * 100)
        else:
            st.warning("銘柄を選択してください。")

with tab2:
    st.header("💰 資産状況とセクター配分")
    
    if not selected_tickers or stock_df.empty:
        st.info("サイドバーから銘柄を選択してください。")
    else:
        # データの構築
        final_portfolio = []
        for _, row in stock_df.iterrows():
            inputs = portfolio_inputs.get(row['銘柄'], {"qty": 0, "price": 0})
            eval_val = inputs['qty'] * row['現在値']
            profit = (row['現在値'] - inputs['price']) * inputs['qty'] if inputs['price'] > 0 else 0
            final_portfolio.append({
                **row, 
                "保有数": inputs['qty'], 
                "取得単価": inputs['price'], 
                "評価額": eval_val, 
                "損益": profit
            })
        
        p_df = pd.DataFrame(final_portfolio)
        
        # 【エラー対策】データが正しく作成されているか確認してから計算
        if not p_df.empty and "評価額" in p_df.columns:
            total_val = p_df['評価額'].sum()
            total_profit = p_df['損益'].sum()
            
            m1, m2 = st.columns(2)
            m1.metric("総評価額", f"{total_val:,.0f}円")
            m2.metric("合計損益", f"{total_profit:,.0f}円", delta=f"{total_profit:,.0f}円")

            if total_val > 0:
                st.subheader("業種別（セクター）配分")
                fig = px.pie(p_df[p_df['保有数'] > 0], values='評価額', names='セクター', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("保有銘柄一覧")
                st.dataframe(p_df[["銘柄", "名称", "セクター", "現在値", "保有数", "評価額", "損益"]].style.format({
                    "現在値": "{:,.1f}", "評価額": "{:,.0f}", "損益": "{:,.0f}"
                }))
            else:
                st.info("左側のサイドバーで「保有数」を入力すると、資産分析グラフが表示されます。")