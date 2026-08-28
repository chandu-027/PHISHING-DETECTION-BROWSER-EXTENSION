import os
import urllib.request
import zipfile
import io

def download_dataset():
    url = "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
        
    zip_path = os.path.join(data_dir, "dataset.zip")
    csv_dest_path = os.path.join(data_dir, "PhiUSIIL_Phishing_URL_Dataset.csv")
    
    if os.path.exists(csv_dest_path):
        print(f"Dataset already exists at: {csv_dest_path}")
        return csv_dest_path
        
    print(f"Downloading dataset from: {url}")
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            print("Download in progress...")
            zip_content = response.read()
            print(f"Successfully downloaded {len(zip_content)} bytes.")
            
            # Save the zip file temporarily or extract directly from memory
            print("Extracting files...")
            with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
                z.extractall(data_dir)
                print(f"Extracted files: {z.namelist()}")
                
        print(f"Dataset download and extraction complete!")
        return csv_dest_path
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None

if __name__ == "__main__":
    download_dataset()
