import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# 1. データの取得
tickers = ["7203.T", "9432.T", "9984.T", "8058.T", "USDJPY=X"]
data = yf.download(tickers, period="1mo")["Close"]

# 2. グラフの全体設定
fig = plt.figure(figsize=(15, 10))
plt.subplots_adjust(hspace=0.4)
fig.suptitle("Weekly Market Analysis Report", fontsize=20, fontweight='bold')

# --- グラフ1: 最新株価の比較 ---
ax1 = plt.subplot(2, 2, 1)
latest_prices = data.iloc[-1].drop("USDJPY=X")
latest_prices.plot(kind='bar', ax=ax1, color='seagreen')
ax1.set_title("Latest Stock Prices (JPY)")
for i, v in enumerate(latest_prices):
    ax1.text(i, v + 50, f"{v:.0f}", ha='center')

# --- グラフ2: トヨタ vs ドル円の相関 ---
ax2 = plt.subplot(2, 2, 2)
norm_data = data / data.iloc[0] * 100
ax2.plot(norm_data.index, norm_data["7203.T"], label="Toyota", color="blue")
ax2.plot(norm_data.index, norm_data["USDJPY=X"], label="USD/JPY", color="orange", linestyle="--")
ax2.set_title("Toyota vs USD/JPY Correlation")
ax2.legend()

# --- グラフ3: 月間騰落率 ---
ax3 = plt.subplot(2, 2, 3)
perf = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
perf.drop("USDJPY=X").plot(kind='bar', ax=ax3, color=['red' if x<0 else 'green' for x in perf])
ax3.set_title("Monthly Performance (%)")
ax3.axhline(0, color='black', linewidth=0.8)

# --- グラフ4: ドル円の推移 ---
ax4 = plt.subplot(2, 2, 4)
ax4.plot(data.index, data["USDJPY=X"], color="firebrick")
ax4.set_title("USD/JPY Exchange Rate")

# 3. 保存
plt.savefig("weekly_auto_report.png")
print("SUCCESS: weekly_auto_report.png has been generated!")