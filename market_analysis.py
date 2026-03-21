import yfinance as yf
import matplotlib.pyplot as plt

# データを取得（トヨタとドル円）
tickers = ["7203.T", "USDJPY=X"]
df = yf.download(tickers, period="1mo")["Close"]

# 開始点を100として正規化
df_norm = df / df.iloc[0] * 100

# グラフ作成
plt.figure(figsize=(10, 6))
plt.plot(df_norm.index, df_norm["7203.T"], label="Toyota", color="blue")
plt.plot(df_norm.index, df_norm["USDJPY=X"], label="USD/JPY", color="orange")

plt.title("Toyota vs USD/JPY (Last 1 Month)")
plt.legend()
plt.grid(True)

# 保存
plt.savefig("market_correlation_fixed.png")
print("SUCCESS: market_correlation_fixed.png created!")