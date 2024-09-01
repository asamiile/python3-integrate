import os
from dotenv import load_dotenv
import requests
import urllib.parse
from datetime import datetime, timedelta
import openai
from openai import OpenAI

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
DISCORD_WEBHOOK_URL_SCHOLAR = os.getenv("DISCORD_WEBHOOK_URL_SCHOLAR")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI APIキーを設定
client = OpenAI(api_key=OPENAI_API_KEY)

# Semantic Scholar APIのエンドポイント
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# 検索クエリの設定
query = "art"
# query = "esthetics"

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
    "fields": "title,authors,tldr,abstract,fieldsOfStudy,venue,publicationDate,url",
    "fieldsOfStudy": "Art,Computer Science,Geology,Psychology,Philosophy,Engineering,Education",
    "limit": 100,
    "publicationDateOrYear": one_day_ago,
}

# APIリクエストを送信
response = requests.get(API_URL, headers=headers, params=params)

# OpenAI APIを使ってテキストを要約する
def summarize_text(text):
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes texts and keeps the summary concise, ideally within 300 characters."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        max_tokens=100,
        temperature=0.5)
        summary = response.choices[0].message.content.strip()
        return summary
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "Error occurred while summarizing text."

# 結果の処理
if response.status_code == 200:
    papers = response.json().get("data", [])

    if not papers:
        print("No search results found.")
    else:
        message = "Semantic Scholar Search Results:\n"
        for paper in papers:
            title = paper.get('title')
            authors = ', '.join(author['name'] for author in paper.get('authors', []))
            tldr = paper.get('tldr').get('text') if paper.get('tldr') else paper.get('abstract', 'No abstract available.')
            abstract = summarize_text(paper.get('abstract', 'No abstract available.'))
            fields_of_study = ', '.join(paper.get('fieldsOfStudy', [])) if paper.get('fieldsOfStudy') else 'No fields of study available'
            venue = paper.get('venue', 'No venue available.')
            publication_date = paper.get('publicationDate')
            url = paper.get('url')

            # Discordに投稿するメッセージを構築
            message += f"**Title:** {title}\n"
            message += f"**Authors:** {authors}\n"
            message += f"**Summary:** {abstract}\n"  # 修正箇所
            message += f"**Fields of Study:** {fields_of_study}\n"
            message += f"**Venue:** {venue}\n"
            message += f"**Publication Date:** {publication_date}\n"
            message += f"**URL:** {url}\n"
            message += "="*75 + "\n"

            print(f"Title: {title}")
            print(f"Authors: {authors}")
            print(f"Summary: {abstract}")  # 修正箇所
            print(f"Fields of Study: {fields_of_study}")
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
