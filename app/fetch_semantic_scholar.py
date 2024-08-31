import os
from dotenv import load_dotenv
import requests
import urllib.parse
from datetime import datetime, timedelta

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Semantic Scholar APIのエンドポイント
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# 検索クエリの設定
query = "Aesthetics"

# キーワードリスト
# keywords = [
#     "art",
#     "Aesthetics",
    # "machine learning",
    # "artificial intelligence",
    # "deep learning",
    # "AI-generated art",
    # "Computer Vision"
# ]

# キーワードをORで結合してクエリを作成
# query = " OR ".join(keywords)

# publicationDateOrYearパラメータに前日の日付を設定
today = datetime.now()
one_day_ago = (today - timedelta(days=1)).strftime('%Y-%m-%d')

# クエリをURLエンコードする
encoded_query = urllib.parse.quote(query)

# APIリクエストヘッダー
headers = {
    "x-api-key": API_KEY
}

# パラメータの設定
params = {
    "query": encoded_query,
    "fields": "title,authors,abstract,tldr,venue,publicationDate,url",
    "fieldsOfStudy": "Art",
    # 'publicationTypes': 'JournalArticle',
    "limit": 100,
    "publicationDateOrYear": one_day_ago,
}

# APIリクエストを送信
response = requests.get(API_URL, headers=headers, params=params)

# 結果の処理
if response.status_code == 200:
    papers = response.json().get("data", [])

    if not papers:
        print("検索結果がありません")
    else:
        for paper in papers:
            print(f"Title: {paper.get('title')}")
            print(f"Authors: {', '.join(author['name'] for author in paper.get('authors', []))}")
            print(f"Abstract: {paper.get('abstract')}")
            print(f"Tldr: {paper.get('tldr')}")
            print(f"Venue: {paper.get('venue')}")
            print(f"Publication Date: {paper.get('publicationDate')}")
            print(f"URL: {paper.get('url')}")

            print("="*80)
else:
    print(f"Error: {response.status_code} - {response.text}")
