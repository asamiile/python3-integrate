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

def fetch_and_notify(query):
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
    if response.status_code != 200:
        print(f"Error fetching data for query '{query}': {response.status_code}")
        return

    data = response.json()

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

    # Discordに通知を送信
    def send_discord_notification(message):
        if DISCORD_WEBHOOK_URL_SCHOLAR:
            data = {"content": message}
            response = requests.post(DISCORD_WEBHOOK_URL_SCHOLAR, json=data)
            if response.status_code != 204:
                print(f"Failed to send notification: {response.status_code}")
                print(f"Response content: {response.content.decode('utf-8')}")
        else:
            print("Discord Webhook URL is not set.")

    # メッセージを分割して送信
    def send_long_message(messages):
        max_length = 2000
        current_message = ""
        for message in messages:
            if len(current_message) + len(message) + 2 > max_length:  # +2 for the "\n\n" separator
                send_discord_notification(current_message)
                current_message = message
            else:
                if current_message:
                    current_message += "\n\n" + message
                else:
                    current_message = message
        if current_message:
            send_discord_notification(current_message)

    # 結果を処理して1つのメッセージにまとめる
    messages = []
    for paper in data.get('data', []):
        title = paper.get('title', 'No title')
        abstract = paper.get('abstract', 'No abstract')
        summary = summarize_text(abstract)
        message = (
            f"**Title:** {title}\n"
            f"**Summary:** {summary}\n"
            f"**Link:** {paper.get('url', 'No URL')}\n"
            f"**Publication Date:** {paper.get('publicationDate', 'No date')}\n"
            f"**Venue:** {paper.get('venue', 'No venue')}\n"
        )
        messages.append(message)

    # まとめたメッセージを送信
    if messages:
        header = f"Semantic Scholar Search Results for {query}:\n"
        send_long_message([header] + messages)

if __name__ == "__main__":
    queries = ["aesthetics", "esthetics", "astronomy", "astrophysics", "environmentology", "philosophy", "poetics"]
    for query in queries:
        fetch_and_notify(query)
