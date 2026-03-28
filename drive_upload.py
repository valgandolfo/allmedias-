import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import mimetypes

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service(credentials_path='credentials.json', token_path='token.json'):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    
    # 1. Variável de ambiente (Modo Produção Railway)
    token_json_str = os.environ.get('GOOGLE_TOKEN_JSON')
    if token_json_str:
        try:
            token_info = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            print(f"Erro ao ler GOOGLE_TOKEN_JSON das vars de ambiente: {e}")

    # 2. Arquivo Local (Modo Desenvolvimento)
    if not creds and os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    return service

def upload_from_stream(service, file_obj, file_name, folder_id=None):
    """Uploads a file-like object to Google Drive and returns the file ID."""
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    mime_type, _ = mimetypes.guess_type(file_name)
    if not mime_type:
        mime_type = 'application/octet-stream'

    media = MediaIoBaseUpload(file_obj, mimetype=mime_type, resumable=True)
    
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def upload_file(service, file_path, folder_id=None):
    """Uploads a file to Google Drive and returns the file ID."""
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    
    if folder_id:
        file_metadata['parents'] = [folder_id]

    # Automatically detect mimetype based on extension or fallback
    media = MediaFileUpload(file_path, resumable=True)
    
    print(f"Uploading {file_name}...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    print(f"File uploaded successfully! Drive File ID: {file_id}")
    
    return file_id

if __name__ == '__main__':
    # Test authentication process
    print("Testing Google Drive Authentication...")
    service = get_drive_service('credentials.json', 'token.json')
    print("Authentication successful!")
    
    # We will need the user to run this script themselves the first time 
    # to open the browser window and authorize the app.
