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

# Function to extract and download images from `a` tags with class `image` in tables
# following an `h2` tag
def download_images_from_section(url, save_dir):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all `h2` tags
    h2_tags = soup.find_all('h2')
    
    for h2 in h2_tags:
        # Find `span` with class `mw-headline` within `h2`
        headline_span = h2.find('span', class_='mw-headline')
        if headline_span:
            # Create a directory based on the `id` attribute of the `span`
            section_id = headline_span.get('id')
            if section_id:
                section_folder = section_id.replace('_', ' ').lower()
                save_dir_path = os.path.join(save_dir, section_folder)
                os.makedirs(save_dir_path, exist_ok=True)

                # Find the next `table` element after the `h2`
                table = h2.find_next_sibling('table')
                
                if table:
                    # Find all `a` tags with class `image` within the table
                    link_tags = table.find_all('a', class_='image')
                    
                    for index, link in enumerate(link_tags, start=1):
                        # Use the href attribute to determine the image URL
                        img_url = link.get('href')
                        if img_url:
                            img_url = urljoin(url, img_url)  # Handle relative URLs
                            download_image(img_url, index, save_dir_path)

# URL of the webpage
url = 'https://dti-dress-to-impress.fandom.com/wiki/Free_items'
# Directory where images will be saved
save_dir = 'free items pt 2'
download_images_from_section(url, save_dir)
