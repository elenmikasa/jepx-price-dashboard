import requests

# 1. 実際のCSV取得用URL
url = "https://www.jepx.jp/_download.php"

# 2. 取得したいパラメータ（必要に応じてファイル名を変更してください）
payload = {
    "dir": "spot_summary",
    "file": "spot_summary_2026.csv"
}

# 3. JEPXのアクセス制限を突破するためのヘッダー
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "Referer": "https://www.jepx.jp/electricpower/market-data/spot/",
    "Origin": "https://www.jepx.jp",
    "Content-Type": "application/x-www-form-urlencoded",
}

# POSTリクエストを送信
print("データをダウンロード中...")
response = requests.post(url, data=payload, headers=headers)

print(f"ステータスコード: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"レスポンスサイズ: {len(response.content)} バイト")

# 4. ステータスコードが200の場合、バイナリとしてそのまま保存
if response.status_code == 200 and len(response.content) > 0:
    filename = payload["file"]
    
    # "wb" (バイナリ書き込みモード) で保存することで、余計な改行変換を一切防ぎます
    with open(filename, "wb") as f:
        f.write(response.content)
        
    print(f"成功: {filename} を正常にダウンロードしました！")
else:
    print("ダウンロードに失敗しました。サーバーからのレスポンス:")
    print(response.text[:300])