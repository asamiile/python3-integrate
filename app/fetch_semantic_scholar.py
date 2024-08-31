import os
from dotenv import load_dotenv
import requests
import urllib.parse
from datetime import datetime, timedelta

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
DISCORD_WEBHOOK_URL_SCHOLAR = os.getenv("DISCORD_WEBHOOK_URL_SCHOLAR")

# Semantic Scholar APIのエンドポイント
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# 検索クエリの設定
query = "art"

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
        message = "No search results found."
        print(message)

    else:
        message = "Semantic Scholar Search Results:\n"
        for paper in papers:
            title = paper.get('title')
            authors = ', '.join(author['name'] for author in paper.get('authors', []))
            abstract = paper.get('abstract', 'No abstract available.')
            tldr = paper.get('tldr').get('text') if paper.get('tldr') else abstract
            venue = paper.get('venue', 'No venue available.')
            publication_date = paper.get('publicationDate')
            url = paper.get('url')

            # Discordに投稿するメッセージを構築
            message += f"**Title:** {title}\n"
            message += f"**Authors:** {authors}\n"
            message += f"**Summary:** {tldr}\n"
            message += f"**Venue:** {venue}\n"
            message += f"**Publication Date:** {publication_date}\n"
            message += f"**URL:** {url}\n"
            message += "="*75 + "\n"

            print(f"Title: {title}")
            print(f"Authors: {authors}")
            print(f"Summary: {tldr}")
            print(f"Venue: {venue}")
            print(f"Publication Date: {publication_date}")
            print(f"URL: {url}")
            print("="*75)

    # Discordにメッセージを送信
    discord_data = {"content": message}
    discord_response = requests.post(DISCORD_WEBHOOK_URL_SCHOLAR, json=discord_data)

    if discord_response.status_code != 204:
        print(f"Failed to send message to Discord: {discord_response.status_code} - {discord_response.text}")

else:
    error_message = f"Error: {response.status_code} - {response.text}"
    print(error_message)

    # エラーもDiscordに送信
    discord_data = {"content": error_message}
    discord_response = requests.post(DISCORD_WEBHOOK_URL_SCHOLAR, json=discord_data)
    if discord_response.status_code != 204:
        print(f"Failed to send error message to Discord: {discord_response.status_code} - {discord_response.text}")
