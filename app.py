import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import urllib.parse
import plotly.express as px

# ページの設定
st.set_page_config(page_title="株式投資・資産管理プロ", layout="wide")

# セクター翻訳辞書
SECTOR_MAP = {
    "Communication Services": "通信サービス",
    "Consumer Cyclical": "一般消費財",
    "Consumer Defensive": "生活必需品",
    "Energy": "エネルギー",
    "Financial Services": "金融",
    "Healthcare": "ヘルスケア",
    "Industrials": "資本財・サービス",
    "Real Estate": "不動産",
    "Technology": "情報技術",
    "Utilities": "公共事業",
    "Basic Materials": "素材",
    "その他": "その他",
    "不明": "不明"
}

# ニュース取得関数
def get_historical_news(keyword, start_date, end_date):
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    return feedparser.parse(url).entries[:5]

# 銘柄詳細をキャッシュ
@st.cache_data(ttl=3600)
def get_stock_details(tickers):
    if not tickers:
        return pd.DataFrame()
    details = []
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            info = tk.info
            details.append({
                "銘柄": t,
                "名称": info.get('shortName') or info.get('longName') or t,
                "sector_en": info.get('sector', 'その他'),
                "現在値": info.get('currentPrice', info.get('regularMarketPrice', 0))
            })
        except:
            details.append({"銘柄": t, "名称": t, "sector_en": "不明", "現在値": 0})
    return pd.DataFrame(details)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定・銘柄管理")
    
    lang_mode = st.radio("表示言語 (セクター名)", ["日本語", "English"], horizontal=True)
    
    # 銘柄追加
    new_code = st.text_input("証券コード追加 (例: 7203)", "").strip()
    
    # 【修正】デフォルトのリストを空に設定
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = []
    
    if st.button("追加"):
        if new_code:
            if new_code.isdigit() and len(new_code) == 4: new_code += ".T"
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
                st.rerun()

    # クリアボタン
    if st.button("リストを全削除"):
        st.session_state.ticker_list = []
        st.rerun()

    selected_tickers = st.multiselect("表示対象", options=st.session_state.ticker_list, default=st.session_state.ticker_list)
    
    st.markdown("---")
    st.subheader("💰 保有状況の入力")
    portfolio_inputs = {}
    
    if selected_tickers:
        with st.spinner("最新データを取得中..."):
            stock_df = get_stock_details(selected_tickers)
        
        for t in selected_tickers:
            match_row = stock_df[stock_df['銘柄'] == t]
            if not match_row.empty:
                row = match_row.iloc[0]
            else:
                row = {"名称": t, "現在値": 0, "sector_en": "不明"}
            
            display_sector = SECTOR_MAP.get(row['sector_en'], row['sector_en']) if lang_mode == "日本語" else row['sector_en']
            
            with st.expander(f"{row['名称']} ({t})", expanded=True):
                qty = st.number_input("保有数", min_value=0, step=1, key=f"sidebar_q_{t}")
                price = st.number_input("取得単価", min_value=0.0, step=1.0, key=f"sidebar_p_{t}")
                # 現在値が0の場合は取得単価を便宜上の評価額に使用するフラグ
                portfolio_inputs[t] = {
                    "qty": qty, "price": price, 
                    "current": row['現在値'] if row['現在値'] > 0 else price, 
                    "name": row['名称'], "sector": display_sector,
                    "real_current": row['現在値']
                }
    else:
        st.info("証券コードを入力して「追加」を押してください。")

    st.markdown("---")
    st.subheader("分析・ニュース設定")
    start_date = st.date_input("分析開始日", datetime.date.today() - datetime.timedelta(days=365))
    news_keyword = st.text_input("ニュースワード", "日本 経済")

# --- メイン画面 ---
st.title("📊 株式総合管理システム")

tab1, tab2 = st.tabs(["📈 株価分析", "💰 ポートフォリオ詳細"])

with tab1:
    if selected_tickers:
        if st.button("分析を実行", type="primary"):
            with st.spinner("チャート作成中..."):
                df = yf.download(selected_tickers, start=start_date, end=datetime.date.today())
                if not df.empty:
                    close_data = df['Close']
                    st.subheader("正規化比較（100基準）")
                    st.line_chart(close_data / close_data.iloc[0] * 100)
    else:
        st.warning("左側のサイドバーで銘柄を追加してください。")

with tab2:
    st.header(f"💰 資産状況とセクター配分")
    
    if not any(v['qty'] > 0 for v in portfolio_inputs.values()):
        st.info("サイドバーで銘柄を追加し、「保有数」を入力すると分析が開始されます。")
    else:
        p_data = []
        for t, val in portfolio_inputs.items():
            if val['qty'] > 0:
                # 現在値が取得できていない場合は取得単価で計算（グラフ表示を維持するため）
                current_price = val['current']
                eval_val = val['qty'] * current_price
                profit = (val['real_current'] - val['price']) * val['qty'] if val['real_current'] > 0 else 0
                
                p_data.append({
                    "銘柄": t, "名称": val['name'], "セクター": val['sector'],
                    "現在値": val['real_current'], "保有数": val['qty'], "評価額": eval_val, "損益": profit
                })
        
        p_df = pd.DataFrame(p_data)
        
        # サマリー
        total_val = p_df['評価額'].sum()
        total_profit = p_df['損益'].sum()
        
        m1, m2 = st.columns(2)
        m1.metric("総評価額", f"{total_val:,.0f}円")
        m2.metric("合計損益", f"{total_profit:,.0f}円", delta=f"{total_profit:,.0f}円")

        # 円グラフ
        st.subheader("業種別（セクター）配分")
        fig = px.pie(p_df, values='評価額', names='セクター', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("保有銘柄一覧")
        st.dataframe(p_df[["銘柄", "名称", "セクター", "現在値", "保有数", "評価額", "損益"]].style.format({
            "現在値": "{:,.1f}", "評価額": "{:,.0f}", "損益": "{:,.0f}"
        }), hide_index=True)

# ニュース（サイドバー）
with st.sidebar:
    st.markdown("---")
    st.subheader("📰 最新経済ニュース")
    news_entries = get_historical_news(news_keyword, start_date, datetime.date.today())
    for entry in news_entries:
        st.markdown(f"**・[{entry.title}]({entry.link})**")