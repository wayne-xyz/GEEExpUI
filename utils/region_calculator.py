"""
Region calculator for GEE export tasks
Implements specific size-based rules for different feature areas
"""

# Description of the region calculator, and the rule of the region size
# <1 ha: 4 ha
# 1-4 ha: 10 ha
# 4-10 ha: 5x ha    
# >10 ha: use the bounds of the region




import ee
from typing import Dict, Any, Tuple

class RegionCalculator:
    def __init__(self):
        # Define area thresholds in hectares
        self.TINY_AREA_THRESHOLD = 1     # < 1 ha
        self.SMALL_AREA_THRESHOLD = 4    # 1-4 ha
        self.MEDIUM_AREA_THRESHOLD = 10  # 4-10 ha
        
        # Define export sizes in square meters
        self.TINY_EXPORT_SIZE = 4 * 10000    # 4 ha for tiny areas
        self.SMALL_EXPORT_SIZE = 10 * 10000   # 10 ha for small areas
        self.MEDIUM_MULTIPLIER = 5           # 5x area for medium areas
        
        # Define scale settings for different sources
        self.SCALE_SETTINGS = {
            'nicfi': 5,
            'sentinel': 10
        }

    def calculate_area(self, geometry: ee.Geometry) -> float:
        """
        Calculate area of geometry in hectares
        Args:
            geometry: ee.Geometry object
        Returns:
            float: Area in hectares
        """
        try:
            area_sqm = geometry.area().getInfo()
            return area_sqm / 10000  # Convert to hectares
        except Exception as e:
            print(f"Error calculating area: {str(e)}")
            return 0

    def get_export_region(self, feature: ee.Feature) -> Tuple[ee.Geometry, float]:
        """
        Calculate export region based on feature size
        Args:
            feature: ee.Feature object
        Returns:
            Tuple of (export_region, shape_size_ha)
        """
        shape_size = self.calculate_area(feature.geometry())
        
        if shape_size < self.MEDIUM_AREA_THRESHOLD:
            if shape_size < self.TINY_AREA_THRESHOLD:
                export_size_sqm = self.TINY_EXPORT_SIZE
            elif shape_size < self.SMALL_AREA_THRESHOLD:
                export_size_sqm = self.SMALL_EXPORT_SIZE
            else:
                export_size_sqm = shape_size * 10000 * self.MEDIUM_MULTIPLIER

            # Create a square region centered on the feature's centroid
            centroid = feature.geometry().centroid()
            half_side_length = (export_size_sqm ** 0.5) / 2
            export_region = centroid.buffer(half_side_length).bounds()
        else:
            # For large areas (>=10 ha), use the feature's actual bounds
            export_region = feature.geometry().bounds()

        return export_region, shape_size

    def format_date_string(self, date_str: str, source_type: str) -> str:
        """Format date string based on source type"""
        if source_type.lower() == 'nicfi':
            return date_str[:7]
        return date_str[:4] + date_str[5:7] + date_str[8:]

    def get_export_settings(self, feature: ee.Feature, source_type: str, date_str: str) -> Dict[str, Any]:
        """
        Get all export settings based on feature and source type
        Args:
            feature: ee.Feature object
            source_type: Type of imagery (nicfi/sentinel)
            date_str: Date string to format
        Returns:
            Dictionary containing all export settings
        """
        # Get export region and shape size
        export_region, shape_size = self.get_export_region(feature)
        
        # Get scale based on source type
        scale = self.SCALE_SETTINGS.get(source_type.lower(), 10)
        
        # Format date string
        formatted_date = self.format_date_string(date_str, source_type)
        
        return {
            'region': export_region,
            'scale': scale,
            'maxPixels': 1e13,
            'crs': 'EPSG:4326',
            'shape_size_ha': shape_size,
            'formatted_date': formatted_date
        }

    def log_settings(self, settings: Dict[str, Any], index: int) -> str:
        """Generate detailed log message for export settings"""
        return f"""
Export Settings for Index {index}:
- Shape Size: {settings['shape_size_ha']:.2f} ha
- Scale: {settings['scale']} meters
- Max Pixels: {settings['maxPixels']}
- CRS: {settings['crs']}
- Date Format: {settings['formatted_date']}
""" 