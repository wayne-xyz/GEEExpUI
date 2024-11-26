# this is the object save the config information to a class based on the yaml file

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple

@dataclass
class Config:
    """Global configuration for GEE Export application"""
    
    # Dynamic Settings from YAML
    shared_assets_id: str = None
    nicfi_image_project: str = None
    sentinel_image_project: str = None
    nicfi_scale: int = None
    sentinel_scale: int = None
    
    # Other settings
    _ee_initialized: bool = False
    yaml_config: Optional[Dict] = None

    @classmethod
    def load_from_yaml(cls, yaml_file=None) -> 'Config':
        """Create config instance with values from YAML file
        
        Args:
            yaml_file: File object or path string to the YAML config file
        """
        try:
            # Handle both file object and file path inputs
            if hasattr(yaml_file, 'read'):
                yaml_config = yaml.safe_load(yaml_file)
            elif isinstance(yaml_file, (str, Path)):
                with open(yaml_file, 'r') as f:
                    yaml_config = yaml.safe_load(f)
            else:
                # Fallback to default template if no file provided
                with open('template_config.yaml', 'r') as f:
                    yaml_config = yaml.safe_load(f)
            
            instance = cls()
            instance.yaml_config = yaml_config
            
            # Load shared assets ID
            instance.shared_assets_id = yaml_config.get('Shared_Assets_ID')
            
            # Load image source settings
            image_sources = yaml_config.get('image_sources', {})
            
            # NICFI settings
            nicfi_config = image_sources.get('nicfi', {})
            instance.nicfi_image_project = nicfi_config.get('project_path')
            instance.nicfi_scale = nicfi_config.get('scale_meters')
            
            # Sentinel settings
            sentinel_config = image_sources.get('sentinel', {})
            instance.sentinel_image_project = sentinel_config.get('project_path')
            instance.sentinel_scale = sentinel_config.get('scale_meters')
            
            return instance
        except Exception as e:
            print(f"Error loading config from YAML: {e}")
            return cls()

    def get_source_info(self, source_type: str) -> Tuple[str, int]:
        """Get project path and scale for the specified source"""
        if source_type.lower() == 'nicfi':
            return self.nicfi_image_project, self.nicfi_scale
        elif source_type.lower() == 'sentinel':
            return self.sentinel_image_project, self.sentinel_scale
        return None, None
    
    def get_config(self):
        return self.yaml_config
    
    def get_image_sources(self):
        return self.yaml_config.get('image_sources', {})
    
    def get_source_name(self, source_type: str) -> str:
        """Get the source name for a specific image source type."""
        return self.yaml_config.get('image_sources', {}).get(source_type, {}).get('source_name', '')
    
    def get_project_path(self, source_type: str) -> str:
        """Get the project path for a specific image source type."""
        return self.yaml_config.get('image_sources', {}).get(source_type, {}).get('project_path', '')
    
    def get_scale_meters(self, source_type: str) -> int:
        """Get the scale in meters for a specific image source type."""
        return self.yaml_config.get('image_sources', {}).get(source_type, {}).get('scale_meters', 0)
    

    def get_shared_assets_id(self):
        """Get the shared assets ID"""
        return self.yaml_config.get('Shared_Assets_ID', '')
    
    def get_drive_settings(self):
        return self.yaml_config.get('drive_settings', {})
    
    def get_export_settings(self):
        return self.yaml_config.get('export_settings', {})   
    
    def get_output_settings(self):
        return self.config.get('output_settings', {})
    
    def get_input_files(self):
        return self.yaml_config.get('input_files', {})       

    
config = Config.load_from_yaml()
