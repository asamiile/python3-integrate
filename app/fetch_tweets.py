import requests
import os
import json
import pandas as pd
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 認証情報の設定
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

if not X_BEARER_TOKEN:
    print("Error: X_BEARER_TOKEN is not set in the .env file.")
    exit(1)

def create_headers(X_BEARER_TOKEN):
    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    return headers

def create_url(keyword, max_results=10):
    search_url = "https://api.twitter.com/2/tweets/search/recent"  # X APIのエンドポイント
    query_params = {
        'query': keyword,  # 検索キーワード
        'max_results': max_results,  # 取得するツイート数
        'tweet.fields': 'created_at,author_id,text',  # 必要なフィールド
    }
    return search_url, query_params

def connect_to_endpoint(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Request returned an error: {response.status_code} {response.text}")
    return response.json()

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    keyword = "香椎浜"  # 検索したいキーワード
    headers = create_headers(X_BEARER_TOKEN)
    url, params = create_url(keyword)
    response_data = connect_to_endpoint(url, headers, params)
    save_to_json(response_data, "tweets.json")

if __name__ == "__main__":
    main()