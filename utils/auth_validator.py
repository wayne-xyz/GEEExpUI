#this is the script to validate the google cloud authentication file

import os

def validate_auth_file(file_path):
    if not os.path.exists(file_path):
        raise ValueError("Invalid or missing service account key file")
    
    try:
        import json
        with open(file_path, 'r') as f:
            credentials = json.load(f)
        
        # Check required fields in service account JSON
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in credentials:
                raise ValueError(f"Missing required field '{field}' in service account key file")
                
        return credentials
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in service account key file")

def check_auth_file(file_path):
    try:
        # Validate JSON structure
        credentials = validate_auth_file(file_path)
        
        # Verify Google Drive access
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            file_path, scopes=SCOPES)
        
        drive_service = build('drive', 'v3', credentials=credentials)
        # Test API call
        drive_service.files().list(pageSize=1).execute()
        
        # Verify Earth Engine access
        import ee
        credentials = ee.ServiceAccountCredentials(credentials.service_account_email, file_path)
        ee.Initialize(credentials)
        
        # Test EE access by making a simple API call
        ee.Number(1).getInfo()
        
        print("Authentication file is valid and has access to Google Drive and Earth Engine")
        return True
        
    except Exception as e:
        print(f"Authentication validation failed: {str(e)}")
        return False

def return_all_folders_with_id(file_path):
    """Return list of available Google Drive folders that files can be saved to"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Get credentials from previously validated auth file
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            file_path, scopes=SCOPES)
        
        # Build Drive service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Query for folders
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)"
        ).execute()
        
        folders = results.get('files', [])
        return [f"{folder['name']} ({folder['id']})" for folder in folders]
        
    except Exception as e:
        print(f"Failed to get Drive folders: {str(e)}")
        return []

