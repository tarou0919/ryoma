import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import urllib.parse

# ページの設定
st.set_page_config(page_title="株式分析プロ", layout="wide")

# ニュース取得関数
def get_historical_news(keyword, start_date, end_date):
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(url)
    return feed.entries[:8]

# 配当情報を取得する関数（表示形式を修正）
def get_dividend_info(tickers):
    div_data = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            ex_div_epoch = info.get('exDividendDate')
            ex_div_date = datetime.datetime.fromtimestamp(ex_div_epoch).date() if ex_div_epoch else "未定"
            
            # 利回りの計算（0.0334 -> 3.34 に変換）
            raw_yield = info.get('dividendYield')
            display_yield = raw_yield * 100 if raw_yield else 0
            
            div_data.append({
                "銘柄": t,
                "配当利回り(%)": display_yield,
                "次回権利落ち日(予定)": ex_div_date,
                "現在の株価": info.get('currentPrice', info.get('regularMarketPrice', 0))
            })
        except:
            continue
    return pd.DataFrame(div_data)

# --- サイドバーの設定 (中身は同じなので省略気味に記載しますが、全コード貼り付けてOKです) ---
with st.sidebar:
    st.header("⚙️ 分析設定")
    st.subheader("銘柄を追加")
    new_code = st.text_input("証券コード (例: 7203, 9432)", "").strip()
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T", "1662.T"]

    if st.button("リストに追加"):
        if new_code:
            if new_code.isdigit() and len(new_code) == 4: new_code += ".T"
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
                st.rerun()
    
    selected_tickers = st.multiselect("分析対象", options=st.session_state.ticker_list, default=st.session_state.ticker_list)
    st.subheader("期間設定")
    today = datetime.date.today()
    start_date = st.date_input("開始日", today - datetime.timedelta(days=365))
    end_date = st.date_input("終了日", today)
    st.subheader("ニュースワード")
    news_keyword = st.text_input("キーワード", "日本 経済")

    st.markdown("---")
    st.header("📰 関連ニュース")
    past_news = get_historical_news(news_keyword, start_date, end_date)
    for entry in past_news:
        st.markdown(f"**・[{entry.title}]({entry.link})**")

# --- メイン画面 ---
st.title("📊 株式・配当・ニュース 統合分析ツール")
tab1, tab2 = st.tabs(["📈 株価・ニュース分析", "📅 配当カレンダー"])

with tab1:
    if st.button("分析を実行", type="primary"):
        with st.spinner("データ取得中..."):
            df = yf.download(selected_tickers, start=start_date, end=end_date)
            data = df['Close'] if isinstance(df.columns, pd.MultiIndex) else df[['Close']]
            if not data.empty:
                st.subheader("正規化比較（100基準）")
                st.line_chart(data / data.iloc[0] * 100)
                st.subheader("相関係数")
                st.dataframe(data.corr().style.background_gradient(cmap='RdYlGn').format("{:.2f}"))

with tab2:
    st.header("📅 配当情報・スケジュール")
    if selected_tickers:
        with st.spinner("配当データ取得中..."):
            div_df = get_dividend_info(selected_tickers)
            if not div_df.empty:
                div_df = div_df.sort_values("次回権利落ち日(予定)", ascending=True)
                
                # 【ここがポイント！】表示形式を整える（小数点2桁など）
                formatted_df = div_df.style.format({
                    "配当利回り(%)": "{:.2f}%",
                    "現在の株価": "{:,.1f}円"
                })
                
                st.write("※権利落ち日の**前営業日**までに株を保有する必要があります。")
                st.table(formatted_df) # スタイルを適用したテーブルを表示
                
                st.info("💡 権利落ち日とは：この日に株を買っても配当はもらえません。前日までに購入しましょう。")
    else:
        st.write("銘柄を選択してください。")