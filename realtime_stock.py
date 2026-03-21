import yfinance as yf
import matplotlib.pyplot as plt

# 取得したい銘柄のリスト（日本の銘柄は ".T" をつけます）
tickers = {
    "KDDI": "9433.T",
    "NTT": "9432.T",
    "Toyota": "7203.T",
    "SoftBank": "9434.T",
    "Mitsubishi": "8058.T",
    "JT": "2914.T",
    "SMBC": "8316.T",
    "TokioMarine": "8766.T"
}

prices = []
names = []

print("Fetching latest stock prices...")

for name, symbol in tickers.items():
    data = yf.Ticker(symbol)
    # 最新の終値を取得
    latest_price = data.history(period="1d")["Close"].iloc[-1]
    prices.append(latest_price)
    names.append(name)
    print(f"{name}: {latest_price:.1f} JPY")

# グラフ作成
plt.figure(figsize=(12, 6))
bars = plt.bar(names, prices, color="darkslategray")

# 棒の上に価格を表示
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 5, f"{yval:,.0f}", ha="center", va="bottom")

plt.title("Real-time Stock Prices (Automatic Fetch)")
plt.ylabel("Stock Price (JPY)")
plt.grid(axis="y", linestyle="--", alpha=0.7)

plt.savefig("realtime_stock_analysis.png")
print("SUCCESS: realtime_stock_analysis.png created!")
