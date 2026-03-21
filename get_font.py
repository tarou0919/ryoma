import urllib.request
url = "https://github.com/googlefonts/mplus-1p/raw/main/fonts/ttf/MPlus1p-Regular.ttf"
urllib.request.urlretrieve(url, "japan.ttf")
print("フォントのダウンロードが完了しました！")