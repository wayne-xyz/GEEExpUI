#this is the script to validate the google cloud authentication file

import os
from google.oauth2 import service_account
import ee

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/earthengine']


def get_credentials(file_path):
    """Get credentials from service account key file"""
    return service_account.Credentials.from_service_account_file(file_path, scopes=SCOPES)



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
    

def initialize_ee(file_path):
    """Initialize Earth Engine with service account credentials"""
    try:
        # Get the general credentials
        credentials = get_credentials(file_path)
        
        # Create EE-specific credentials
        ee_credentials = ee.ServiceAccountCredentials(
            credentials.service_account_email,
            file_path
        )
        
        # Initialize EE with project ID
        ee.Initialize(ee_credentials, project='stone-armor-430205-e2')
        
        # Test EE connection
        ee.Number(1).getInfo()
        print("Earth Engine initialized successfully")
        return True
        
    except Exception as e:
        print(f"Failed to initialize EE: {str(e)}")
        return False





def check_assets_exist():
    json_file_path = "stone-armor-430205-e2-2cd696d4afcd.json"
    SHARED_ASSETS_ID = "projects/ee-qinheyi/assets/1823_ADRSM"
    """Check if an asset exists in the user's GEE account"""
    initialize_ee(json_file_path)
    shape_file_table=ee.FeatureCollection(SHARED_ASSETS_ID)
    
    print(f"The shapefile table has {shape_file_table.size().getInfo()} features")



if __name__ == "__main__":
    check_assets_exist()
    pass

