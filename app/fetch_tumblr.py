import os
import json
from datetime import datetime, timedelta
import pytumblr
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def load_env_variables():
    load_dotenv()
    env_vars = {
        "api_key": os.getenv("TUMBLR_API_KEY"),
        "service_account_file": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "folder_id": os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    }
    missing_vars = [key for key, value in env_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
    return env_vars

def create_drive_service(service_account_file):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def upload_to_drive(service, file_path, folder_id):
    file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")} uploaded to Google Drive.')

def search_tumblr(client, keywords):
    data = []
    today = datetime.now()
    start_time = int((today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_time = int((today - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999).timestamp())

    for keyword in keywords:
        try:
            posts = client.tagged(keyword)
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
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"tumblr_{datetime.now().strftime('%Y%m%d')}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")
    return filename

if __name__ == "__main__":
    try:
        env_vars = load_env_variables()
        drive_service = create_drive_service(env_vars['service_account_file'])
        client = pytumblr.TumblrRestClient(env_vars['api_key'])

        keywords = ["香椎浜", "Kashiihama", "かしいはま", "アイランドシティ", "照葉", "てりは"]
        results = search_tumblr(client, keywords)

        file_path = save_data_to_json(results)
        if file_path:
            upload_to_drive(drive_service, file_path, env_vars['folder_id'])
            os.remove(file_path)
    except Exception as e:
        print(f"An error occurred: {e}")
