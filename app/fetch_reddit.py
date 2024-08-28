import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import praw

# .envファイルから環境変数を読み込む
load_dotenv()

def get_reddit_client():
    """Reddit APIクライアントを取得する"""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    if not client_id or not client_secret or not user_agent:
        raise EnvironmentError("Reddit API credentials are not set in the .env file.")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

def create_drive_service():
    """Google Drive APIクライアントを作成"""
    google_credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not google_credentials_json:
        raise EnvironmentError("Google Drive credentials are not set in the environment variables.")

    service_account_info = json.loads(google_credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=['https://www.googleapis.com/auth/drive.file']
    )
    return build('drive', 'v3', credentials=credentials)

def upload_to_drive(service, file_path, folder_id):
    """ファイルをGoogle Driveにアップロード"""
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

def search_reddit(reddit, keywords):
    """Redditからデータを検索して保存"""
    data = []
    now = datetime.utcnow()
    start_time = datetime(now.year, now.month, now.day) - timedelta(days=1)
    end_time = start_time + timedelta(days=1)

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
        return None

    output_dir = Path('data/reddit')
    output_dir.mkdir(parents=True, exist_ok=True)

    current_date = now.strftime('%Y%m%d')
    output_file = output_dir / f'reddit_{current_date}.json'

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Failed to save data: {e}")
        return None

def main():
    """メイン処理"""
    keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
    reddit = get_reddit_client()
    file_path = search_reddit(reddit, keywords)

    if file_path:
        drive_service = create_drive_service()
        google_drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        upload_to_drive(drive_service, file_path, google_drive_folder_id)

if __name__ == '__main__':
    main()
