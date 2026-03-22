import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. ページの設定（デザインの土台）
st.set_page_config(page_title="株式相関分析プロ", layout="wide")

# サイドバーのデザイン設定
with st.sidebar:
    st.header("⚙️ 分析設定")
    
    # 銘柄の選択機能
    stock_options = {
        "日本電信電話 (NTT)": "9432.T",
        "KDDI": "9433.T",
        "伊藤忠商事": "8001.T",
        "三菱商事": "8058.T",
        "トヨタ自動車": "7203.T",
        "日経平均 (225)": "^N225"
    }
    
    selected_stocks = st.multiselect(
        "比較する銘柄を選んでください",
        options=list(stock_options.keys()),
        default=["日本電信電話 (NTT)", "KDDI"]
    )
    
    # 期間の設定
    years = st.slider("分析期間（年）", 1, 5, 2)

# メイン画面のタイトル
st.title("📊 株式・指数 相関分析プロ")
st.caption(f"選択された銘柄の直近 {years} 年間の相関を可視化します")

if st.button("分析を開始する", type="primary"):
    if len(selected_stocks) < 2:
        st.error("分析には2つ以上の銘柄を選んでください。")
    else:
        with st.spinner("データを取得中..."):
            # データの取得
            tickers = [stock_options[s] for s in selected_stocks]
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.DateOffset(years=years)
            
            data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
            
            # グラフの描画
            st.subheader("📈 株価推移（正規化）")
            # 比較しやすくするために開始点を100として計算
            norm_data = (data / data.iloc[0] * 100)
            st.line_chart(norm_data)
            
            # 相関係数の計算
            st.subheader("🔢 相関係数")
            corr = data.corr()
            st.write("1に近いほど同じ動き、-1に近いほど逆の動きをします。")
            st.dataframe(corr.style.background_gradient(cmap='RdYlGn'))
            
            st.balloons() # 成功の演出