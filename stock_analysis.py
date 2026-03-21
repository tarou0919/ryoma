import pandas as pd
import matplotlib.pyplot as plt

# データを読み込む
df = pd.read_csv("stock_data.csv")

# グラフの設定
fig, ax1 = plt.subplots(figsize=(10, 6))

# 棒グラフ（配当金）
ax1.bar(df["銘柄"], df["配当"], color="seagreen", label="Dividend")
ax1.set_ylabel("Dividend (Yen)")

# 折れ線グラフ（利回り）
ax2 = ax1.twinx()
ax2.plot(df["銘柄"], df["利回り"], color="orange", marker="o", label="Yield")
ax2.set_ylabel("Yield (%)")

plt.title("Stock Analysis: Dividend & Yield")
plt.savefig("stock_analysis_final.png")
print("SUCCESS: stock_analysis_final.png created!")
