import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import urllib.parse

# ページの設定
st.set_page_config(page_title="株式自由分析プロ + 期間ニュース", layout="wide")

# ニュース取得関数の改善（期間とキーワードに対応）
def get_historical_news(keyword, start_date, end_date):
    # Googleニュースの検索RSSを利用
    # 期間指定のパラメータを付与して検索効率を上げます
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    
    feed = feedparser.parse(url)
    return feed.entries[:10]  # 最大10件表示

# サイドバーの設定
with st.sidebar:
    st.header("⚙️ 分析設定")
    
    # 1. 銘柄追加
    st.subheader("銘柄を追加")
    new_code = st.text_input("証券コード (例: 7203, AAPL)", "").strip()
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T"]
    if st.button("リストに追加"):
        if new_code:
            if new_code.isdigit() and len(new_code) == 4: new_code += ".T"
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
    
    selected_tickers = st.multiselect("分析対象", options=st.session_state.ticker_list, default=st.session_state.ticker_list)

    # 2. 期間設定
    st.subheader("期間を設定")
    today = datetime.date.today()
    start_date = st.date_input("開始日", today - datetime.timedelta(days=365))
    end_date = st.date_input("終了日", today)

    # 3. ニュース検索用キーワード
    st.subheader("ニュース検索ワード")
    news_keyword = st.text_input("気になる言葉 (例: 日銀, 半導体, 増配)", "日本 経済")

    # ニュース表示
    st.markdown("---")
    st.header("📰 指定期間のニュース")
    with st.spinner("ニュースを検索中..."):
        past_news = get_historical_news(news_keyword, start_date, end_date)
        if past_news:
            for entry in past_news:
                st.markdown(f"**・[{entry.title}]({entry.link})**")
                st.caption(f"{entry.published[:16]}")
        else:
            st.write("該当するニュースが見つかりませんでした。")

# メイン画面
st.title("📊 期間連動型：株式・ニュース分析ツール")

if st.button("分析を開始する", type="primary"):
    if len(selected_tickers) < 2:
        st.error("2つ以上の銘柄を選んでください。")
    else:
        with st.spinner("株価データ取得中..."):
            try:
                df = yf.download(selected_tickers, start=start_date, end=end_date)
                data = df['Close'] if isinstance(df.columns, pd.MultiIndex) else df[['Close']]
                
                if not data.empty:
                    data = data.ffill()
                    st.subheader(f"📈 {start_date} ～ {end_date} の推移")
                    st.line_chart(data / data.iloc[0] * 100)
                    
                    st.subheader("🔢 相関係数")
                    st.dataframe(data.corr().style.background_gradient(cmap='RdYlGn').format("{:.2f}"))
                    st.balloons()
            except Exception as e:
                st.error(f"エラー: {e}")