import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ページの設定
st.set_page_config(page_title="配当3案同時比較ツール", layout="wide")

# 配当情報を取得する関数
def get_dividend_data(tickers):
    data_list = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            raw_yield = info.get('dividendYield', 0)
            if raw_yield is None: raw_yield = 0
            
            # 利回りの単位調整
            display_yield = raw_yield * 100 if raw_yield < 0.2 else raw_yield
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            data_list.append({
                "銘柄": t,
                "利回り": display_yield,
                "株価": price
            })
        except:
            continue
    return data_list

# メイン画面
st.title("⚖️ 高配当投資：3案同時シミュレーション")
st.caption("3つの異なるポートフォリオ案を作成し、配当利回りや予想配当額を比較します。")

# 3つのカラムを作成
col1, col2, col3 = st.columns(3)

# 各案の入力と表示
plans = [
    {"name": "案 A", "col": col1, "key": "plan_a", "default": ["9432.T", "9433.T"]},
    {"name": "案 B", "col": col2, "key": "plan_b", "default": ["8058.T", "8001.T"]},
    {"name": "案 C", "col": col3, "key": "plan_c", "default": ["1662.T", "8316.T"]}
]

for plan in plans:
    with plan["col"]:
        st.subheader(f"📍 {plan['name']}")
        
        # 銘柄入力
        ticker_input = st.text_area(
            f"{plan['name']}の銘柄コード (カンマ区切り)", 
            value=",".join(plan["default"]), 
            key=f"input_{plan['key']}"
        )
        tickers = [t.strip() for t in ticker_input.split(",") if t.strip()]
        
        # 投資予算入力
        budget = st.number_input(f"{plan['name']}の投資予算 (円)", min_value=0, value=1000000, step=100000, key=f"budget_{plan['key']}")
        
        if st.button(f"{plan['name']}を計算", key=f"btn_{plan['key']}"):
            with st.spinner("データ取得中..."):
                results = get_dividend_data(tickers)
                if results:
                    df = pd.DataFrame(results)
                    avg_yield = df["利回り"].mean()
                    est_dividend = budget * (avg_yield / 100)
                    
                    # 結果表示
                    st.metric("平均利回り", f"{avg_yield:.2f}%")
                    st.metric("年間配当予想", f"{est_dividend:,.0f} 円")
                    
                    # 内訳テーブル
                    st.write("---")
                    st.write("▼ 銘柄内訳")
                    formatted_df = df.style.format({"利回り": "{:.2f}%", "株価": "{:,.1f}円"})
                    st.table(formatted_df)
                else:
                    st.error("データが取得できませんでした。")

st.write("---")
st.info("💡 銘柄コードは '7203.T' のように入力してください。数字4桁の場合は、後で自動補完機能を追加することも可能です。")