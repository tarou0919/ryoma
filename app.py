import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ページの設定
st.set_page_config(page_title="株式自由分析プロ", layout="wide")

# サイドバーの設定
with st.sidebar:
    st.header("⚙️ 分析設定")
    
    # 銘柄コードの入力エリア
    st.subheader("1. 銘柄を追加")
    new_code = st.text_input("証券コードを入力 (例: 7203, AAPL)", "").strip()
    
    # セッション状態で銘柄リストを管理
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ["9432.T", "9433.T"] # 初期値

    if st.button("リストに追加"):
        if new_code:
            # 数字4桁の場合は自動で .T を付与
            if new_code.isdigit() and len(new_code) == 4:
                new_code += ".T"
            
            if new_code not in st.session_state.ticker_list:
                st.session_state.ticker_list.append(new_code)
                st.success(f"{new_code} を追加しました")
            else:
                st.warning("既に追加されています")

    # 現在のリスト表示とリセット
    selected_tickers = st.multiselect(
        "分析対象を選択",
        options=st.session_state.ticker_list,
        default=st.session_state.ticker_list
    )
    
    if st.button("リストをクリア"):
        st.session_state.ticker_list = []
        st.rerun()

    st.subheader("2. 期間を設定")
    today = datetime.date.today()
    three_years_ago = today - datetime.timedelta(days=365*3)
    start_date = st.date_input("開始日", three_years_ago)
    end_date = st.date_input("終了日", today)

# メイン画面
st.title("📊 株式・指数 自由相関分析")
st.caption("証券コードを自由に入力して、複数の銘柄の動きを比較・分析できます。")

if st.button("分析を開始する", type="primary"):
    if len(selected_tickers) < 2:
        st.error("分析には2つ以上の銘柄を選んでください。左のサイドバーからコードを入力して追加できます。")
    elif start_date >= end_date:
        st.error("開始日は終了日より前の日付を選択してください。")
    else:
        with st.spinner("最新データを取得中..."):
            try:
                # データのダウンロード
                df = yf.download(selected_tickers, start=start_date, end=end_date)
                
                # yfinanceの最新仕様(MultiIndex)に対応
                if isinstance(df.columns, pd.MultiIndex):
                    data = df['Close']
                else:
                    data = df[['Close']]

                if data.empty or data.isnull().all().all():
                    st.warning("データが取得できませんでした。コードが正しいか確認してください。")
                else:
                    # 欠損値を補完
                    data = data.ffill()
                    
                    # 1. 株価推移グラフ
                    st.subheader("📈 株価推移（比較用：開始日を100として正規化）")
                    norm_data = (data / data.iloc[0] * 100)
                    st.line_chart(norm_data)
                    
                    # 2. 相関係数の表示
                    st.subheader("🔢 銘柄間の相関係数")
                    st.write("1に近いほど同じ動き、-1に近いほど逆の動きをします。")
                    corr = data.corr()
                    st.dataframe(corr.style.background_gradient(cmap='RdYlGn').format("{:.2f}"))
                    
                    # 3. 生データの表示
                    with st.expander("取得した生データを確認"):
                        st.dataframe(data)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")