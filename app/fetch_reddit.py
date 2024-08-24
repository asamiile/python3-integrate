import praw
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の確認
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")

if not client_id or not client_secret:
    print("Error: Reddit API credentials are not set in the .env file.")
    exit(1)

# Reddit APIのクレデンシャルを設定
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="my_reddit_app/0.1 by your_username"
)

def search_reddit(keywords):
    data = []

    # 前日の0時〜23:59の範囲を計算
    now = datetime.utcnow()
    start_time = datetime(now.year, now.month, now.day) - timedelta(days=1)
    end_time = start_time + timedelta(days=1)

    for keyword in keywords:
        subreddit = reddit.subreddit('all')
        results = subreddit.search(keyword, limit=100)  # 検索結果を増やす
        for submission in results:
            submission_time = datetime.utcfromtimestamp(submission.created_utc)
            if not (start_time <= submission_time < end_time):
                continue
            post_data = {
                'title': submission.title,
                'selftext': submission.selftext,
                'created_utc': submission_time.strftime('%Y-%m-%d %H:%M:%S'),
                'url': submission.url,
                'comments': []
            }
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                comment_data = {
                    'body': comment.body,
                    'created_utc': datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                }
                post_data['comments'].append(comment_data)
            data.append(post_data)

    if not data:
        print("No data found, skipping save.")
        return

    output_dir = Path('data/reddit')
    if not output_dir.exists():
        print(f"Creating directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # 現在の日付を取得してファイル名に組み込む
    current_date = now.strftime('%Y%m%d')
    output_file = output_dir / f'reddit_{current_date}.json'
    print(f"Output file path: {output_file}")

    # JSONファイルに保存
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Failed to save data: {e}")

if __name__ == "__main__":
    search_keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    search_reddit(search_keywords)