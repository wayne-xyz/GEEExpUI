from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import yaml
import json
from dataclasses import dataclass

@dataclass
class InputFiles:
    auth_file: Path = None
    config_file: Path = None
    target_file: Path = None

class FileManager:
    def __init__(self):
        self.input_files = InputFiles()
        self.selected_folders = []

    def load_auth_file(self, file_path):
        try:
            self.input_files.auth_file = Path(file_path)
            return True
        except Exception as e:
            print(f"Error loading auth file: {e}")
            return False

    def load_config(self, file_path):
        try:
            self.input_files.config_file = Path(file_path)
            return True
        except Exception as e:
            print(f"Error loading config file: {e}")
            return False

    def load_target_list(self, file_path):
        try:
            self.input_files.target_file = Path(file_path)
            return True
        except Exception as e:
            print(f"Error loading target file: {e}")
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
        if self.input_files.target_file is not None:
            # Read the CSV file from the Path object
            target_csv_df = pd.read_csv(self.input_files.target_file)
            # Assuming the first column contains the indices
            target_field = target_csv_df.columns[0]
            # Convert the column to a list
            return target_csv_df[target_field].tolist()
        return []

    def get_shape_attributes(self, index: int) -> Dict:
        """Get shapefile attributes for a specific index"""
        if self.shapefile_data is not None:
            row = self.shapefile_data[self.shapefile_data['Index'] == index]
            if not row.empty:
                return row.iloc[0].to_dict()
        return {} 