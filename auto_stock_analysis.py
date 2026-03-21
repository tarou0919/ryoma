import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. 取得したい銘柄のリスト（日本株は末尾に .T をつけます）
tickers = {
    "9433.T": "KDDI",
    "9432.T": "NTT",
    "7203.T": "Toyota",
    "9984.T": "SoftBank",
    "8058.T": "Mitsubishi"
}

print("Fetching latest stock prices...")

# 2. データを自動取得
data = []
for symbol, name in tickers.items():
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")["Close"].iloc[-1]
    data.append({"Name": name, "Price": round(price, 1)})

df = pd.DataFrame(data)

# 3. グラフ作成
plt.figure(figsize=(10, 6))
bars = plt.bar(df["Name"], df["Price"], color="teal")
plt.bar_label(bars, padding=3)
plt.title("Real-time Stock Prices (Auto-Fetched)")
plt.ylabel("Price (JPY)")

# 4. 保存
plt.savefig("auto_fetched_prices.png")
print("SUCCESS: auto_fetched_prices.png created with latest data!")
