from typing import Tuple, Dict, Any
from pathlib import Path
import yaml

class ConfigValidator:
    """Validator for YAML configuration files"""
    
    @staticmethod
    def validate_yaml_content(yaml_content: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate the content of the YAML configuration
        Args:
            yaml_content: Dictionary containing YAML configuration
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Validate image_sources section
            if 'image_sources' not in yaml_content:
                return False, "Missing 'image_sources' section in YAML"

            image_sources = yaml_content['image_sources']
            
            # Validate NICFI configuration
            if not ConfigValidator._validate_source_config(image_sources, 'nicfi'):
                return False, "Invalid NICFI configuration"
                
            # Validate Sentinel configuration
            if not ConfigValidator._validate_source_config(image_sources, 'sentinel'):
                return False, "Invalid Sentinel configuration"

            # Validate Shared Assets ID
            if 'Shared_Assets_ID' not in yaml_content:
                return False, "Missing 'Shared_Assets_ID' in YAML"
            if not isinstance(yaml_content['Shared_Assets_ID'], str):
                return False, "Invalid type for 'Shared_Assets_ID', expected string"
            if not yaml_content['Shared_Assets_ID'].startswith('projects/'):
                return False, "'Shared_Assets_ID' must start with 'projects/'"

            return True, "Configuration is valid"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def _validate_source_config(image_sources: Dict[str, Any], source_type: str) -> bool:
        """
        Validate configuration for a specific image source
        Args:
            image_sources: Dictionary containing image source configurations
            source_type: Type of image source ('nicfi' or 'sentinel')
        Returns:
            bool: True if configuration is valid
        """
        if source_type not in image_sources:
            return False
            
        source_config = image_sources[source_type]
        required_fields = {
            'source_name': str,
            'project_path': str,
            'scale_meters': int
        }
        
        for field, field_type in required_fields.items():
            if field not in source_config:
                return False
            if not isinstance(source_config[field], field_type):
                return False
                
        return True

    @staticmethod
    def validate_yaml_file(file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate a YAML configuration file
        Args:
            file_path: Path to YAML file
        Returns:
            Tuple[bool, str, Dict]: (is_valid, error_message, yaml_content)
        """
        try:
            # Check file exists
            if not Path(file_path).exists():
                return False, f"File not found: {file_path}", None

            # Load YAML content
            with open(file_path, 'r') as f:
                yaml_content = yaml.safe_load(f)

            # Validate content
            is_valid, message = ConfigValidator.validate_yaml_content(yaml_content)
            return is_valid, message, yaml_content if is_valid else None

        except yaml.YAMLError as e:
            return False, f"Invalid YAML format: {str(e)}", None
        except Exception as e:
            return False, f"Validation error: {str(e)}", None

def validate_config(config_path: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Utility function to validate configuration file
    Args:
        config_path: Path to configuration file
    Returns:
        Tuple[bool, str, Dict]: (is_valid, error_message, yaml_content)
    """
    validator = ConfigValidator()
    return validator.validate_yaml_file(config_path) 