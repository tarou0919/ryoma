import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import urllib.parse

# ページの設定
st.set_page_config(page_title="株式分析プロ + 配当カレンダー", layout="wide")

# ニュース取得関数
def get_historical_news(keyword, start_date, end_date):
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(url)
    return feed.entries[:8]

# 配当情報を取得する関数
def get_dividend_info(tickers):
    div_data = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            # 次回の権利落ち日を取得（データがない場合はNone）
            ex_div_epoch = info.get('exDividendDate')
            ex_div_date = datetime.datetime.fromtimestamp(ex_div_epoch).date() if ex_div_epoch else "未定"
            
            div_data.append({
                "銘柄": t,
                "配当利回り(%)": round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else "不明",
                "次回権利落ち日(予定)": ex_div_date,
                "現在の株価": info.get('currentPrice', info.get('regularMarketPrice', "不明"))
            })
        except:
            continue
    return pd.DataFrame(div_data)

# サイドバーの設定
with st.sidebar:
    st.header("⚙️ 分析設定")
    
    st.subheader("銘柄を追加")
    new_code = st.text_input("証券コード (例: 7203, 9432)", "").strip()
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T", "8058.T"] # 初期値に三菱商事などを追加

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

    st.subheader("ニュース検索ワード")
    news_keyword = st.text_input("キーワード", "日本 経済")

    st.markdown("---")
    st.header("📰 関連ニュース")
    past_news = get_historical_news(news_keyword, start_date, end_date)
    for entry in past_news:
        st.markdown(f"**・[{entry.title}]({entry.link})**")
        st.caption(f"{entry.published[:16]}")

# メイン画面
st.title("📊 株式・配当・ニュース 統合分析ツール")

# タブ機能で画面をスッキリさせる
tab1, tab2 = st.tabs(["📈 株価・ニュース分析", "📅 配当カレンダー"])

with tab1:
    if st.button("分析を実行", type="primary"):
        if len(selected_tickers) < 2:
            st.error("比較のために2つ以上の銘柄を選んでください。")
        else:
            with st.spinner("データ取得中..."):
                df = yf.download(selected_tickers, start=start_date, end=end_date)
                data = df['Close'] if isinstance(df.columns, pd.MultiIndex) else df[['Close']]
                if not data.empty:
                    st.subheader("正規化比較（100を基準とした推移）")
                    st.line_chart(data / data.iloc[0] * 100)
                    st.subheader("相関係数")
                    st.dataframe(data.corr().style.background_gradient(cmap='RdYlGn').format("{:.2f}"))

with tab2:
    st.header("📅 配当情報・スケジュール")
    if selected_tickers:
        with st.spinner("配当データ取得中..."):
            div_df = get_dividend_info(selected_tickers)
            if not div_df.empty:
                # 利回りが高い順に並び替え
                div_df = div_df.sort_values("次回権利落ち日(予定)", ascending=True)
                
                st.write("※権利落ち日の**前営業日**までに株を保有する必要があります。")
                st.table(div_df)
                
                st.info("💡 権利落ち日とは：この日に株を買っても、その期の配当はもらえません。前日までに購入しましょう。")
            else:
                st.warning("配当情報が見つかりませんでした。")
    else:
        st.write("サイドバーから銘柄を選択してください。")