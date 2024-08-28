import praw
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から設定を読み込む
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
google_drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not client_id or not client_secret:
    print("Error: Reddit API credentials are not set in the .env file.")
    exit(1)

if not google_drive_folder_id or not service_account_file:
    print("Error: Google Drive credentials are not set in the .env file.")
    exit(1)

# Google Drive APIクライアントを作成
def create_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    return service

# ファイルをGoogle Driveにアップロード
def upload_to_drive(service, file_path, folder_id):
    file_metadata = {
        'name': file_path.name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"File ID: {file.get('id')} uploaded to Google Drive.")

# Redditからデータを検索して保存
def search_reddit(keywords):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent='your_user_agent'
    )

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

    # Google Driveにアップロード
    drive_service = create_drive_service()
    upload_to_drive(drive_service, output_file, google_drive_folder_id)

# メインの処理
if __name__ == '__main__':
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    search_reddit(keywords)