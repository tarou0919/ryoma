import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ページの設定
st.set_page_config(page_title="株式相関分析プロ", layout="wide")

# サイドバーの設定
with st.sidebar:
    st.header("⚙️ 分析設定")
    
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
    
    # 【新機能】カレンダーによる期間設定
    today = datetime.date.today()
    three_years_ago = today - datetime.timedelta(days=365*3)
    
    start_date = st.date_input("開始日", three_years_ago)
    end_date = st.date_input("終了日", today)

# メメイン画面
st.title("📊 株式・指数 相関分析プロ")

if st.button("分析を開始する", type="primary"):
    if len(selected_stocks) < 2:
        st.error("分析には2つ以上の銘柄を選んでください。")
    elif start_date >= end_date:
        st.error("開始日は終了日より前の日付を選択してください。")
    else:
        with st.spinner("データを取得中..."):
            tickers = [stock_options[s] for s in selected_stocks]
            
            # yfinanceの最新仕様に合わせたデータ取得
            df = yf.download(tickers, start=start_date, end=end_date)
            
            # データのクリーニング（エラー対策）
            if 'Close' in df.columns:
                data = df['Close']
            else:
                data = df
            
            if data.empty:
                st.warning("指定された期間のデータが見つかりませんでした。")
            else:
                # 1. 株価推移グラフ
                st.subheader("📈 株価推移（正規化）")
                st.info("開始時点を100として比較しています。マウスを乗せると詳細が見れます。")
                norm_data = (data / data.iloc[0] * 100)
                st.line_chart(norm_data)
                
                # 2. 相関係数の表示
                st.subheader("🔢 相関係数テーブル")
                corr = data.corr()
                st.dataframe(corr.style.background_gradient(cmap='RdYlGn').format("{:.2f}"))
                
                # 3. データのダウンロード機能
                csv = data.to_csv().encode('utf-8-sig')
                st.download_button(
                    label="CSV形式でデータを保存",
                    data=csv,
                    file_name=f"stock_analysis_{today}.csv",
                    mime='text/csv',
                )
                st.balloons()