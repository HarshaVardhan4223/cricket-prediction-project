import zipfile
import os

print("Extracting all cricket data...")

# List of zip files to extract
zip_files = [
    ('data/raw/ipl_data.zip', 'data/raw/ipl/'),
    ('data/raw/odi_data.zip', 'data/raw/odi/'),
    ('data/raw/t20_data.zip', 'data/raw/t20/')
]

for zip_path, extract_path in zip_files:
    if os.path.exists(zip_path):
        print(f"\nExtracting {zip_path}...")
        
        # Create folder if doesn't exist
        os.makedirs(extract_path, exist_ok=True)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Count files
        files = os.listdir(extract_path)
        csv_files = [f for f in files if f.endswith('.csv')]
        
        print(f"✅ Extracted {len(csv_files)} CSV files to {extract_path}")
    else:
        print(f"❌ {zip_path} not found!")

print("\n🎉 All data extracted successfully!")