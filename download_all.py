import requests
import zipfile
import os
from datetime import datetime

# URL to your live zip file
url = "https://liars-poker-uploader.onrender.com/files.zip"

# Create timestamp for this run
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Where to save the zip file temporarily
zip_filename = f"liars_poker_results_{timestamp}.zip"

# Folder to extract into (e.g., synced_results/20250723_151400/)
extract_folder = os.path.join("synced_results", timestamp)
os.makedirs(extract_folder, exist_ok=True)

try:
    print(f"Downloading results from: {url}")
    response = requests.get(url)
    if response.ok:
        with open(zip_filename, "wb") as f:
            f.write(response.content)
            print(f"ZIP file size: {os.path.getsize(zip_filename)} bytes")
        print(f"Downloaded ZIP as: {zip_filename}")

        # Extract contents
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            print("Files inside ZIP:")
            print(zip_ref.namelist())
            zip_ref.extractall(extract_folder)
        print(f"Extracted into: {extract_folder}")

        # Optionally delete zip
        os.remove(zip_filename)
        print("ZIP file deleted after extraction.")

    else:
        print(f"Failed to download. Status code: {response.status_code}")

except Exception as e:
    print(f"Error during download or extraction: {e}")