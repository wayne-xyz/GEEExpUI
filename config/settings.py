import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
STATIC_DIR = PROJECT_ROOT / "static"
DATA_DIR = STATIC_DIR / "data"

# Google Earth Engine settings
SERVICE_ACCOUNT_KEY_FILE = 'stone-armor-430205-e2-2cd696d4afcd.json'
EE_PROJECT_ID = "stone-armor-430205-e2"
SHARED_ASSETS_ID = "projects/ee-qinheyi/assets/1823_ADRSM"

# Image source settings
NICFI_IMAGE_PROJECT = 'projects/planet-nicfi/assets/basemaps/americas'
SENTINEL_IMAGE_PROJECT = 'COPERNICUS/S2_SR_HARMONIZED'

# Task settings
MAX_CONCURRENT_TASKS = 2000
TASK_CHECK_INTERVAL = 600  # seconds

# File paths
TASK_YAML_FILE_PATH = DATA_DIR / 'update_task.yaml'
EXPORT_TARGET_SHAPE_INDEX_FILE_PATH = DATA_DIR / 'Target_index.csv'
SHAPEFILE_DATA_PATH = DATA_DIR / 'Shapefile_data_20240819.csv'

# Alternative service account key file for different OS
if not os.path.exists(SERVICE_ACCOUNT_KEY_FILE):
    SERVICE_ACCOUNT_KEY_FILE = 'stone-armor-430205-e2-9913c17acb94.json'

# Create required directories
for directory in [STATIC_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 