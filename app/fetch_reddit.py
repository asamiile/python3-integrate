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

def get_env_variable(var_name, error_message):
    value = os.getenv(var_name)
    if not value:
        print(error_message)
        exit(1)
    return value

# 環境変数から設定を読み込む
client_id = get_env_variable('REDDIT_CLIENT_ID', "Error: Reddit API credentials are not set in the .env file.")
client_secret = get_env_variable('REDDIT_CLIENT_SECRET', "Error: Reddit API credentials are not set in the .env file.")
google_drive_folder_id = get_env_variable('GOOGLE_DRIVE_FOLDER_ID', "Error: Google Drive credentials are not set in the .env file.")
service_account_file = get_env_variable('GOOGLE_APPLICATION_CREDENTIALS', "Error: Google Drive credentials are not set in the .env file.")

# Google Drive APIクライアントを作成
def create_drive_service(service_account_file):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

# ファイルをGoogle Driveにアップロード
def upload_to_drive(service, file_path, folder_id):
    file_metadata = {'name': file_path.name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')} uploaded to Google Drive.")

# ディレクトリの作成とJSONファイルの保存
def save_data_to_json(data, output_dir, file_name):
    if not output_dir.exists():
        print(f"Creating directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / file_name
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Failed to save data: {e}")
    return output_file

# Redditからデータを検索して保存
def search_reddit(keywords):
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='your_user_agent')
    data = []

    # 前日の0時から23:59までのタイムスタンプを計算
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    start_time = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_time = int(yesterday.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp())

    for keyword in keywords:
        subreddit = reddit.subreddit('all')
        results = subreddit.search(keyword, limit=100)
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
    current_date = now.strftime('%Y%m%d')
    output_file = save_data_to_json(data, output_dir, f'reddit_{current_date}.json')

    drive_service = create_drive_service(service_account_file)
    upload_to_drive(drive_service, output_file, google_drive_folder_id)

# メインの処理
if __name__ == '__main__':
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    search_reddit(keywords)