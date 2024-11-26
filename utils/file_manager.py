from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import yaml
import json
from dataclasses import dataclass

@dataclass
class InputFiles:
    config_path: Path
    auth_file: Path
    target_list: Path
    shapefile_data: Path

class FileManager:
    def __init__(self):
        self.config: Dict = {}
        self.target_list: Optional[pd.DataFrame] = None
        self.shapefile_data: Optional[pd.DataFrame] = None
        self.auth_credentials: Dict = {}
        self.input_files: Optional[InputFiles] = None

    def load_config(self, config_path: str) -> bool:
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading config file: {e}")
            return False

    def load_auth_file(self, auth_path: str) -> bool:
        """Load Google Cloud authentication JSON file"""
        try:
            with open(auth_path, 'r') as f:
                self.auth_credentials = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading authentication file: {e}")
            return False

    def load_target_list(self, target_path: str) -> bool:
        """Load target shapefile list CSV"""
        try:
            self.target_list = pd.read_csv(target_path)
            return True
        except Exception as e:
            print(f"Error loading target list: {e}")
            return False

    def load_shapefile_data(self, shapefile_path: str) -> bool:
        """Load shapefile attributes CSV"""
        try:
            self.shapefile_data = pd.read_csv(shapefile_path)
            return True
        except Exception as e:
            print(f"Error loading shapefile data: {e}")
            return False

    def load_all_files(self, config_path: str) -> bool:
        """Load all required files"""
        if not self.load_config(config_path):
            return False

        input_files = self.config.get('input_files', {})
        
        self.input_files = InputFiles(
            config_path=Path(config_path),
            auth_file=Path(input_files['auth_file']),
            target_list=Path(input_files['target_list']),
            shapefile_data=Path(input_files['shapefile_data'])
        )

        return all([
            self.load_auth_file(str(self.input_files.auth_file)),
            self.load_target_list(str(self.input_files.target_list)),
            self.load_shapefile_data(str(self.input_files.shapefile_data))
        ])

    def get_target_indices(self) -> List[int]:
        """Get list of target indices from target list"""
        if self.target_list is not None:
            return self.target_list['Index'].tolist()
        return []

    def get_shape_attributes(self, index: int) -> Dict:
        """Get shapefile attributes for a specific index"""
        if self.shapefile_data is not None:
            row = self.shapefile_data[self.shapefile_data['Index'] == index]
            if not row.empty:
                return row.iloc[0].to_dict()
        return {} 