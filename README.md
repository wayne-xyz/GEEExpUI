# GEEExpUI

A user-friendly desktop application for exporting high-resolution TIFF files from Google Earth Engine (GEE) to Google Drive.

## Features

- Export high-resolution TIFF files from Google Earth Engine to Google Drive
- Support for multiple data sources (NICFI, Sentinel)
- Flexible export parameters:
  - Time range selection
  - Shape region rules based on shapefiles
  - Scale and resolution settings
  - Google Earth Engine project source selection
- Google Cloud authentication support
- Task management with progress monitoring
- User-friendly Tkinter GUI
- YAML-based configuration

## Screenshot

![Screenshot](https://github.com/wayne-xyz/GEEExpUI/blob/main/Screenshot.png)

[Youtube](https://youtu.be/_ddzpUMCEuw?si=r9cFgoJEDYVLAoxn)

## Known Issues
- Google Drive Shared folder issue: A folder shared with the service account email, then the folder is deleted and the folder still exists in the List of account available list, but can not be accessed and save the files to the folder.

## Requirements

- Python 3.11
- Google Earth Engine account
- Google Cloud project with necessary APIs enabled
- Required Python packages (see requirements.txt)

## Installation

1. Setup Google Cloud Project and GEE Account 
   - Create a new project in Google Cloud 
   - Enable the Earth Engine API
   - Create a new service account and download the JSON key file (Step 1, Google Cloud Authentication file)
   - Setup GEE Account and upload a shapefile as shared asset 
   - Get the Asset ID of the shapefile and the Project ID of the Image collection (Step 2, Google Earth Engine Asset ID and Project ID as Yaml file)
   - Setup a index file of the target indices based on the Shapefile (Step 3, Target Indices as csv file)
   - Share the Google Drive's folder with the service account email (GCP project service account email in the json file)



2. Setup the Python Environment
   - Install the required Python packages
   - Prepare the 3 files, json, yaml, csv.

3. Make sure the Drive Folder have enought space to save the exported files.

4. Run the main.py



