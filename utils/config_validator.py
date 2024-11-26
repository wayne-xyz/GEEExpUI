import yaml
from pathlib import Path
from typing import Dict, Any
import os
from datetime import datetime

class ConfigValidator:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config file: {e}")

    def validate(self) -> bool:
        """Run all validation checks"""
        try:
            self._validate_google_cloud()
            self._validate_drive_settings()
            self._validate_image_sources()
            self._validate_export_settings()
            self._validate_paths()
            return True
        except ValueError as e:
            print(f"Configuration validation failed: {e}")
            return False

    def _validate_google_cloud(self):
        """Validate Google Cloud settings"""
        gc = self.config.get('google_cloud', {})
        
        # Check service account key file
        key_file = gc.get('service_account_key_file')
        if not key_file or not os.path.exists(key_file):
            raise ValueError("Invalid or missing service account key file")

        # Check required fields
        required = ['project_id', 'shared_assets_id']
        for field in required:
            if not gc.get(field):
                raise ValueError(f"Missing required Google Cloud setting: {field}")

    def _validate_drive_settings(self):
        """Validate Google Drive settings"""
        drive = self.config.get('drive_settings', {})
        folders = drive.get('folders', {})
        
        if not all([folders.get('nicfi'), folders.get('sentinel')]):
            raise ValueError("Missing required Drive folder settings")

    def _validate_image_sources(self):
        """Validate image source settings"""
        sources = self.config.get('image_sources', {})
        
        for source in ['nicfi', 'sentinel']:
            if source not in sources:
                raise ValueError(f"Missing {source} configuration")
            
            source_config = sources[source]
            required = ['project_path', 'scale_meters', 'bands']
            for field in required:
                if field not in source_config:
                    raise ValueError(f"Missing {field} in {source} configuration")

    def _validate_export_settings(self):
        """Validate export settings"""
        export = self.config.get('export_settings', {})
        required = ['max_concurrent_tasks', 'task_check_interval', 'max_pixels', 'crs']
        
        for field in required:
            if field not in export:
                raise ValueError(f"Missing export setting: {field}")

    def _validate_paths(self):
        """Validate file paths"""
        paths = self.config.get('paths', {})
        
        for path_name, path_value in paths.items():
            if path_name in ['shapefile_data', 'target_index']:
                if not os.path.exists(path_value):
                    raise ValueError(f"Required file not found: {path_value}")

def validate_config(config_path: str) -> bool:
    """Utility function to validate configuration file"""
    validator = ConfigValidator(config_path)
    return validator.validate() 