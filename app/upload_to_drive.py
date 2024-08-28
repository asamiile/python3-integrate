import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# .envファイルから環境変数を読み込む
load_dotenv()

def upload_to_drive(file_path, folder_id):
    # 環境変数からサービスアカウントファイルのパスを取得
    service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    if not service_account_file:
        raise ValueError("環境変数 'GOOGLE_APPLICATION_CREDENTIALS' が設定されていません。")

    # Google Drive APIのクライアントを作成
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)

    # ファイルをアップロード
    file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")

if __name__ == '__main__':
    file_path = 'data/test/test.json'
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

    if not folder_id:
        raise ValueError("環境変数 'GOOGLE_DRIVE_FOLDER_ID' が設定されていません。")

    upload_to_drive(file_path, folder_id)