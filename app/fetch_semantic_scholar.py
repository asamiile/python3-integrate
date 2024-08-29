import os
from dotenv import load_dotenv
import requests
import urllib.parse

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Semantic Scholar APIのエンドポイント
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# 複数キーワードでの検索クエリの設定
query = "art AND ('artificial intelligence' OR 'machine learning' OR 'deep learning' OR 'AI-generated art')"

# クエリをURLエンコードする
encoded_query = urllib.parse.quote(query)

# APIリクエストヘッダー
headers = {
    "x-api-key": API_KEY
}

# パラメータの設定
params = {
    "query": encoded_query,
    "fields": "title,authors,abstract,year,venue,url",
    "limit": 10  # 取得する論文数
}

# APIリクエストを送信
response = requests.get(API_URL, headers=headers, params=params)

# 結果の処理
if response.status_code == 200:
    papers = response.json().get("data", [])
    for paper in papers:
        print(f"Title: {paper.get('title')}")
        print(f"Authors: {', '.join(author['name'] for author in paper.get('authors', []))}")
        print(f"Abstract: {paper.get('abstract')}")
        print(f"Year: {paper.get('year')}")
        print(f"Venue: {paper.get('venue')}")
        print(f"URL: {paper.get('url')}")

        print("="*80)
else:
    print(f"Error: {response.status_code} - {response.text}")
