import os
import json
from datetime import datetime, timedelta
import pytumblr
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の確認
api_key = os.getenv("TUMBLR_API_KEY")

if not api_key:
    print("Error: Tumblr API key is not set in the .env file.")
    exit(1)

# Tumblr APIのクライアントを設定
client = pytumblr.TumblrRestClient(api_key)

def search_tumblr(keywords):
    data = []

    # 前日の0時から23:59までのタイムスタンプを計算
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    start_time = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_time = int(yesterday.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp())

    # キーワードに基づいてTumblrの投稿を検索
    for keyword in keywords:
        try:
            posts = client.tagged(keyword)
            if not posts:
                print(f"No posts found for keyword: {keyword}")
            for post in posts:
                if start_time <= post.get('timestamp', 0) <= end_time:
                    data.append({
                        'post_url': post.get('post_url'),
                        'timestamp': post.get('timestamp'),
                        'summary': post.get('summary'),
                        'type': post.get('type'),
                        'tags': post.get('tags'),
                        'title': post.get('title'),
                        'body': post.get('body'),
                        'photos': post.get('photos'),
                        'caption': post.get('caption'),
                        'player': post.get('player'),
                        'audio_url': post.get('audio_url')
                    })
        except Exception as e:
            print(f"Error fetching posts for keyword '{keyword}': {e}")

    return data

def save_data_to_json(data, directory="data/tumblr"):
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, f"tumblr_{datetime.now().strftime('%Y%m%d')}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    results = search_tumblr(keywords)
    save_data_to_json(results)