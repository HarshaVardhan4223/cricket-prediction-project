import requests
import zipfile
import os

def download_cricsheet_data():
    """Download latest T20 and ODI data"""
    
    urls = {
        't20': 'https://cricsheet.org/downloads/t20s_csv2.zip',
        'odi': 'https://cricsheet.org/downloads/odis_csv2.zip',
        'ipl': 'https://cricsheet.org/downloads/ipl_csv2.zip'
    }
    
    for format_type, url in urls.items():
        print(f"Downloading {format_type} data...")
        response = requests.get(url)
        
        zip_path = f'data/raw/{format_type}_data.zip'
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(f'data/raw/{format_type}/')
        
        print(f"{format_type} data downloaded!")

download_cricsheet_data()