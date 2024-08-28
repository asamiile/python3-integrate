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
google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not client_id or not client_secret:
    print("Error: Reddit API credentials are not set in the .env file.")
    exit(1)

if not google_drive_folder_id:
    print("Error: Google Drive folder ID is not set in the .env file.")
    exit(1)

if not google_credentials_path:
    print("Error: Google Drive credentials path is not set in the .env file.")
    exit(1)

# Google Drive APIクライアントを作成
def create_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(
        google_credentials_path, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

# Google Driveにファイルをアップロード
def upload_to_drive(service, file_path, folder_id):
    file_metadata = {
        'name': file_path.name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/json')
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"File ID: {file.get('id')}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

# 前日の0時から23:59までのデータを取得するための時間範囲を計算
def get_yesterday_time_range():
    end_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=1)
    return start_time, end_time

# Redditからデータを検索して保存
def search_reddit(keywords):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent='fetch_reddit/v1.0 (by asamiile)'
    )
    start_time, end_time = get_yesterday_time_range()
    data = []

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
    return data

# データをJSONファイルに保存
def save_data_to_json(data, directory="data/reddit"):
    if not data:  # データがない時は保存しない
        return None

    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)

    filename = directory_path / f"reddit_{datetime.now().strftime('%Y%m%d')}.json"
    with filename.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")
    return filename

# メインの処理
if __name__ == '__main__':
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    results = search_reddit(keywords)
    file_path = save_data_to_json(results)

    if file_path:  # 保存成功時のみアップロード
        drive_service = create_drive_service()
        upload_to_drive(drive_service, file_path, google_drive_folder_id)
        os.remove(file_path)
    else:
        print("No data file created, nothing to upload.")