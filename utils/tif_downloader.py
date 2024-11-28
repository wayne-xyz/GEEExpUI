"""
TIF Downloader module for handling Google Earth Engine exports
Supports both NICFI and Sentinel imagery with different time intervals
"""

from datetime import datetime, timedelta
import time
from typing import List, Tuple
import ee
from pathlib import Path
import pandas as pd
from utils.auth_validator import get_credentials
from utils.region_calculator import RegionCalculator

class TifDownloader:
    """Main class for downloading TIF files from Google Earth Engine"""
    
    def __init__(self, config, auth_file, target_indices, start_date, end_date, source_type,log_callback=None):
        """
        Initialize TIF downloader
        Args:
            config: Configuration object containing settings
            auth_file: Path to authentication file
            target_indices: List of target indices to process
        """
        self.config = config
        self.auth_file = Path(auth_file)
        self.target_indices = target_indices
        self.task_count = 0  # only used for current batch
        self.all_task_count = 0
        self.current_task_index = 0 # for all the total at end 
        self.pending_tasks = []
        self.MAX_CONCURRENT_TASKS = 2000
        self.TASK_CHECK_INTERVAL = 600  # 10 minutes in seconds
        self.start_date = start_date
        self.end_date = end_date
        self.source_type = source_type
        self.log_callback = log_callback

        self.region_calculator = RegionCalculator()

        # Validate inputs
        if not self.auth_file.exists():
            raise FileNotFoundError(f"Auth file not found: {self.auth_file}")
        if not self.target_indices:
            raise ValueError("No target indices provided")
        
        self.all_task_count = self.calculate_total_tasks()


    def log_message(self, message):
        """Log a message to the console"""
        print(message)
        if self.log_callback:
            self.log_callback(message)
       


    def calculate_total_tasks(self):
        """Calculate total tasks based on date ranges and target indices"""
        date_ranges = self.get_date_ranges(self.start_date, self.end_date, self.source_type)

        return len(date_ranges) * len(self.target_indices)

    def initialize_ee(self):
        """Initialize Earth Engine with credentials"""
        try:
            credentials = get_credentials(self.auth_file)
            ee.Initialize(credentials)
            print("Earth Engine initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Earth Engine: {str(e)}")

    def get_date_ranges(self, start_date: str, end_date: str, source_type: str) -> List[Tuple[str, str]]:
        """
        Get list of date ranges based on source type
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            source_type: Type of imagery (nicfi/sentinel)
        Returns:
            List of (start_date, end_date) tuples
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")

        dates = []
        if source_type.lower() == 'nicfi':
            # One image per month for NICFI
            current = start.replace(day=1)
            while current < end:
                next_month = (current + timedelta(days=32)).replace(day=1)
                dates.append((current.strftime("%Y-%m-%d"), next_month.strftime("%Y-%m-%d")))
                current = next_month
        else:
            # Three images per month for Sentinel
            current = start
            while current < end:
                month_end = current.replace(day=28) + timedelta(days=4)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                
                # Split month into three periods
                dates.extend([
                    (current.strftime("%Y-%m-%d"), 
                     (current.replace(day=10)).strftime("%Y-%m-%d")),
                    (current.replace(day=11).strftime("%Y-%m-%d"), 
                     (current.replace(day=20)).strftime("%Y-%m-%d")),
                    (current.replace(day=21).strftime("%Y-%m-%d"), 
                     month_end.strftime("%Y-%m-%d"))
                ])
                current = (month_end + timedelta(days=1))

        return dates

    def get_image_collection(self, date_range: Tuple[str, str], source_type: str) -> ee.ImageCollection:
        """
        Get image collection for specified date range and source
        Args:
            date_range: (start_date, end_date) tuple
            source_type: Type of imagery (nicfi/sentinel)
        Returns:
            ee.ImageCollection: Filtered image collection
        """
        start_date, end_date = date_range
        collection_id = self.config.get_project_path(source_type)
        
        return (ee.ImageCollection(collection_id)
                .filterDate(start_date, end_date)
                .median())

    def create_export_task(self, index: int, image: ee.Image, date_range: Tuple[str, str], 
                          source_type: str, folder_name: str):
        """
        Create and submit an export task
        Args:
            index: Shape index
            image: Earth Engine image to export
            date_range: (start_date, end_date) tuple
            source_type: Type of imagery
            folder_name: Google Drive folder name
        """
        start_date, end_date = date_range
        
        try:
            # Get feature from shared asset
            feature = (ee.FeatureCollection(self.config.get_shared_assets_id())
                      .filter(ee.Filter.eq('Index', index))
                      .first())
            

            export_region,export_size_ha = self.region_calculator.get_export_region(feature)
            print(f"export_region size: {export_size_ha}")

            # Set export parameters based on source type
            scale = 5 if source_type.lower() == 'nicfi' else 10
            date_str = start_date[:7] if source_type.lower() == 'nicfi' else start_date.replace('-', '')

            # Create export task
            task = ee.batch.Export.image.toDrive(
                image=image.clip(export_region),
                description=f"export_{index}_{date_str}",
                folder=folder_name,
                scale=scale,
                region=export_region,
                crs='EPSG:4326',
                maxPixels=1e13,
                fileNamePrefix=f"{index}-{date_str}-{source_type}"
            )

            # Start the task
            task.start()
            self.current_task_index += 1



            self.task_count += 1
            self.pending_tasks.append(task)

            self.log_message(f"Task submitted - Total: {self.all_task_count}, Current: {self.current_task_index}, Index: {index}, Date: {start_date} to {end_date}, Source: {source_type}, Folder: {folder_name}, ID: {task.id}")

        except Exception as e:
            print(f"Error creating task for index {index}: {str(e)}")
            raise

    def is_ee_task_list_clear(self):
        """Check if GEE task list is clear for new submissions"""
        try:
            tasks = ee.batch.Task.list()
            active_tasks = [task for task in tasks if task.state in ['READY', 'RUNNING']]
            print(f"\nCurrent active GEE tasks: {len(active_tasks)}")
            return len(active_tasks) < self.MAX_CONCURRENT_TASKS
        except Exception as e:
            print(f"Error checking GEE task list: {str(e)}")
            return False

    def monitor_tasks(self):
        """Monitor GEE tasks and wait until task list is clear"""
        while not self.is_ee_task_list_clear():
            self.log_message(f"\nWaiting {self.TASK_CHECK_INTERVAL/60:.1f} minutes before checking GEE task status...")
            time.sleep(self.TASK_CHECK_INTERVAL)
            
            try:
                tasks = ee.batch.Task.list()
                active_tasks = [task for task in tasks if task.state in ['READY', 'RUNNING']]
                
                print(f"""
GEE Task Status:
- Active Tasks: {len(active_tasks)}
- Maximum Allowed: {self.MAX_CONCURRENT_TASKS}
- Space Available: {self.MAX_CONCURRENT_TASKS - len(active_tasks)}
                """)
                
            except Exception as e:
                print(f"Error monitoring tasks: {str(e)}")
        
        print("\nGEE task list is clear for new submissions")

    def start_export(self, start_date: str, end_date: str, source_type: str, folder_name: str):
        """Start the export process with batch task submission"""
        print(f"""
Starting Export Process:
- Source Type: {source_type}
- Date Range: {start_date} to {end_date}
- Target Indices: {len(self.target_indices)}
- Save Folder: {folder_name}
    """)

        try:
            # Get all date ranges to process
            date_ranges = self.get_date_ranges(start_date, end_date, source_type)
            print(f"Generated {len(date_ranges)} date ranges to process")

            batch_count = 0
            for date_range in date_ranges:
                # Get image collection for this date range
                collection = self.get_image_collection(date_range, source_type)

                for index in self.target_indices:
                    try:
                        # Check if we've hit the batch limit
                        if self.task_count >= self.MAX_CONCURRENT_TASKS:
                            batch_count += 1
                            print(f"\nBatch {batch_count} completed ({self.task_count} tasks)")
                            print("Waiting for tasks to complete before starting next batch...")
                            self.monitor_tasks()
                            self.task_count = 0  # Reset counter for next batch
                            self.pending_tasks = []  # Clear pending tasks list

                        # Create and submit task
                        self.create_export_task(index, collection, date_range, source_type, folder_name)

                    except Exception as e:
                        print(f"Error processing index {index}: {str(e)}")
                        continue

            # Wait for final batch to complete
            if self.task_count > 0:
                batch_count += 1
                print(f"\nFinal batch {batch_count} submitted ({self.task_count} tasks)")
                print("Waiting for final tasks to complete...")
                self.monitor_tasks()

            self.log_message(f"""
Export Process Summary:
- Total Batches: {batch_count}
- Total Date Ranges: {len(date_ranges)}
- Total Indices: {len(self.target_indices)}
- Total Tasks Created: {self.current_task_index}
            """)

        except Exception as e:
            self.log_message(f"Error during export process: {str(e)}")
            raise


def main():
    """Example usage of TifDownloader"""
    pass

if __name__ == "__main__":
    main()
    
