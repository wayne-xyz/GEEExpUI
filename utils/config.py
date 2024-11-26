# this is the object save the config information to a class based on the yaml file

import yaml
from pathlib import Path

class Config:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
        
    def get_config(self):
        return self.config
    
    def get_image_sources(self):
        return self.config.get('image_sources', {})
    
    def get_source_name(self, source_type: str) -> str:
        """Get the source name for a specific image source type."""
        return self.config.get('image_sources', {}).get(source_type, {}).get('source_name', '')
    
    def get_project_path(self, source_type: str) -> str:
        """Get the project path for a specific image source type."""
        return self.config.get('image_sources', {}).get(source_type, {}).get('project_path', '')
    
    def get_scale_meters(self, source_type: str) -> int:
        """Get the scale in meters for a specific image source type."""
        return self.config.get('image_sources', {}).get(source_type, {}).get('scale_meters', 0)
    
    def get_drive_settings(self):
        return self.config.get('drive_settings', {})
    
    def get_export_settings(self):
        return self.config.get('export_settings', {})   
    
    def get_output_settings(self):
        return self.config.get('output_settings', {})
    
    def get_input_files(self):
        return self.config.get('input_files', {})       

        