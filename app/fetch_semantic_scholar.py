import os
from dotenv import load_dotenv
import requests
import urllib.parse
from datetime import datetime

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Semantic Scholar APIのエンドポイント
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# 現在の年を取得
current_year = datetime.now().year

# 検索クエリの設定
query = "Aesthetics"

# キーワードリスト
# keywords = [
#     "art",
#     "machine learning",
#     "artificial intelligence",
#     "deep learning",
#     "AI-generated art",
#     "Computer Vision"
# ]

# キーワードをORで結合してクエリを作成
# query = " OR ".join(keywords)

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
    "fieldsOfStudy": "Art",
    "limit": 100,
    'year': f'{current_year}-',
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
