# upload_to_drive.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def upload_to_drive(file_path, folder_id):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')

if __name__ == '__main__':
    file_path = 'data/test/test.json'
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    upload_to_drive(file_path, folder_id)