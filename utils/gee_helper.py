import ee
from utils.auth_validator import get_credentials

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


def return_assets_size(file_path, asset_id):
    initialize_ee(file_path)
    shape_file_table=ee.FeatureCollection(asset_id)
    return shape_file_table.size().getInfo()



if __name__ == "__main__":
    json_file_path = "stone-armor-430205-e2-2cd696d4afcd.json"
    SHARED_ASSETS_ID = "projects/ee-qinheyi/assets/1823_ADRSM"
    print(return_assets_size(json_file_path, SHARED_ASSETS_ID))


