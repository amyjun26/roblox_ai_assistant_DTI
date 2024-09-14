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

# Function to extract and download images from `a` tags with class `image`
def download_images_from_links(url, save_dir):
    # Create the directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all `a` tags with class `image`
    link_tags = soup.find_all('a', class_='image')
    
    for index, link in enumerate(link_tags, start=1):
        # Use the href attribute to determine the image URL
        img_url = link.get('href')
        if img_url:
            img_url = urljoin(url, img_url)  # Handle relative URLs
            download_image(img_url, index, save_dir)

# URL of the webpage
url = 'https://dti-dress-to-impress.fandom.com/wiki/Free_items'
# Directory where images will be saved
save_dir = 'free_items'
download_images_from_links(url, save_dir)
