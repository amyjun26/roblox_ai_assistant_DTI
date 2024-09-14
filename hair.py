import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Function to download and save an image
def download_image(img_url, index, save_dir):
    try:
        img_response = requests.get(img_url, stream=True)
        img_response.raise_for_status()  # Check for request errors
        
        # Generate filename based on index
        img_name = f"item{index}.jpg"
        img_path = os.path.join(save_dir, img_name)

        with open(img_path, 'wb') as file:
            for chunk in img_response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Downloaded: {img_url} to {img_path}")
    except requests.RequestException as e:
        print(f"Error downloading {img_url}: {e}")

# Function to extract and download images from `a` tags in the second `td` of each `tr`
def download_images_from_table(url, save_dir):
    # Create the directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all `tr` tags
    rows = soup.find_all('tr')
    
    for index, row in enumerate(rows, start=1):
        # Find all `td` tags in the row
        tds = row.find_all('td')
        if len(tds) > 1:
            # Get the `a` tag in the second `td`
            a_tag = tds[1].find('a')
            if a_tag:
                # Use the href attribute to determine the image URL
                img_url = a_tag.get('href')
                if img_url:
                    img_url = urljoin(url, img_url)  # Handle relative URLs
                    download_image(img_url, index, save_dir)

# URL of the webpage
url = 'https://dti-dress-to-impress.fandom.com/wiki/Hairs'
# Directory where images will be saved
save_dir = 'hair'
download_images_from_table(url, save_dir)
