import pandas as pd
import matplotlib.pyplot as plt

# データを読み込む
df = pd.read_csv("performance_data.csv")

# 騰落率（%）を計算
df["騰落率"] = ((df["現在値"] - df["一ヶ月前"]) / df["一ヶ月前"]) * 100

# グラフの設定
plt.figure(figsize=(12, 6))
# プラスなら緑、マイナスなら赤に色分け
colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in df["騰落率"]]
bars = plt.bar(df["銘柄"], df["騰落率"], color=colors, edgecolor="black", alpha=0.8)

# 棒の先端にパーセンテージを表示
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + (0.2 if yval > 0 else -0.5), 
             f"{yval:+.1f}%", va="center", ha="center", fontweight="bold")

plt.axhline(0, color="black", linewidth=1) # 0%の基準線
plt.title("Monthly Stock Performance Analysis", fontsize=16)
plt.ylabel("Price Change (%)")
plt.grid(axis="y", linestyle="--", alpha=0.5)

# 保存
plt.savefig("stock_performance.png")
print("SUCCESS: stock_performance.png created!")
