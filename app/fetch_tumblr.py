import os
import json
from datetime import datetime, timedelta
import pytumblr
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の確認
api_key = os.getenv("TUMBLR_API_KEY")
service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

if not api_key:
    print("Error: Tumblr API key is not set in the .env file.")
    exit(1)

if not service_account_file or not folder_id:
    print("Error: Google Drive credentials or folder ID is not set in the .env file.")
    exit(1)

# 環境変数からGoogle認証情報のファイルパスを取得
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Tumblr APIのクライアントを設定
client = pytumblr.TumblrRestClient(api_key)

# Google Drive APIの設定
SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(file_path, file_name, folder_id):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f'File ID: {file.get("id")}')

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

def save_data_to_json(data, directory="/tmp"):
    if not data:
        print("No data found, skipping save.")
        return None

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, f"tumblr_{datetime.now().strftime('%Y%m%d')}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")
    return filename

if __name__ == "__main__":
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    results = search_tumblr(keywords)
    file_path = save_data_to_json(results)
    if file_path:
        upload_to_drive(file_path, os.path.basename(file_path), folder_id)
        os.remove(file_path)