import ee
from utils.auth_validator import get_credentials
import pandas as pd

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


def compare_target_asset(credentials_file_path, target_csv, shared_asset_id):
    # the csv file contains the list of the a field which also in the shared asset's shapefile table.
    # 1step. does this field exist in the shared asset's shapefile table?
    # 2step. if it does, how many features are there in the shared asset's shapefile table?
    # 3step. compare the number of features between the target asset and the shared asset
    result_str=""
    # 1step
    initialize_ee(credentials_file_path)
    shared_asset_table=ee.FeatureCollection(shared_asset_id)
    shared_asset_table_size=shared_asset_table.size().getInfo()
    # get the target_csv's field's name
    target_csv_df=pd.read_csv(target_csv)
    target_field=target_csv_df.columns[0]
    # check if this field exists in the shared asset's shapefile table
    if target_field in shared_asset_table.getInfo()['features'][0]['properties']:
        # 2step
        shared_asset_field_size=shared_asset_table.getInfo()['features'][0]['properties'][target_field]
    else:
        result_str="The field does not exist in the shared asset's shapefile table"
        return result_str
    
    # compare all the target's rows value with the shared asset's shapefile table's field value 
    target_csv_df = pd.read_csv(target_csv)
    total_target_count = len(target_csv_df)
    matched_count = 0
    
    # Get all features from shared asset table
    features = shared_asset_table.getInfo()['features']
    
    # Check each target value against all features
    for index, row in target_csv_df.iterrows():
        target_value = row[0]
        for feature in features:
            if str(target_value) == str(feature['properties'][target_field]):
                matched_count += 1
                break
    
    result_str = f"Total target values: {total_target_count}\n"
    result_str += f"Number of target values found in shared asset: {matched_count}\n"
    result_str += f"Number of target values not found: {total_target_count - matched_count}"
    
    return result_str










    pass



if __name__ == "__main__":
    json_file_path = "stone-armor-430205-e2-2cd696d4afcd.json"
    SHARED_ASSETS_ID = "projects/ee-qinheyi/assets/1823_ADRSM"
    print(return_assets_size(json_file_path, SHARED_ASSETS_ID))


