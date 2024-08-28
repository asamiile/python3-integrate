import os
import json
from datetime import datetime, timedelta
import pytumblr
from dotenv import load_dotenv
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から設定を読み込む
api_key = os.getenv('TUMBLR_API_KEY')
google_drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not api_key:
    print("Error: Tumblr API key is not set in the .env file.")
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

# Tumblrからデータを検索して保存
def search_tumblr(client, keywords):
    start_time, end_time = get_yesterday_time_range()
    data = []
    for keyword in keywords:
        posts = client.tagged(keyword, before=end_time.timestamp(), filter='text')
        for post in posts:
            post_time = datetime.fromtimestamp(post['timestamp'])
            if start_time <= post_time <= end_time:
                data.append({
                    'blog_name': post['blog_name'],
                    'id': post['id'],
                    'post_url': post['post_url'],
                    'type': post['type'],
                    'timestamp': post['timestamp'],
                    'date': post['date'],
                    'tags': post['tags'],
                    'note_count': post['note_count'],
                })
    return data

# データをJSONファイルに保存
def save_data_to_json(data, directory="data/tumblr"):
    if not data:  # データが空の時は保存しない
        print("No data found, skipping save.")
        return None

    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)

    filename = directory_path / f"tumblr_{datetime.now().strftime('%Y%m%d')}.json"
    with filename.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")
    return filename

# メインの処理
if __name__ == "__main__":
    client = pytumblr.TumblrRestClient(api_key)
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    results = search_tumblr(client, keywords)
    file_path = save_data_to_json(results)

    if file_path:  # 保存成功時のみアップロード
        drive_service = create_drive_service()
        upload_to_drive(drive_service, file_path, google_drive_folder_id)
        os.remove(file_path)
    else:
        print("No data file created, nothing to upload.")