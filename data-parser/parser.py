import os
from dotenv import load_dotenv
import requests
import csv
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

# Load environment variables
load_dotenv()

# ButterCMS API URL and Auth Token
base_api_url = "https://api.buttercms.com/v2/pages/"
auth_token = os.getenv('BUTTERCMS_API_KEY')
web_host = os.getenv('WEB_HOST')

def clean_html_to_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ').strip()
        return text
    except Exception as e:
        print(f"Error cleaning HTML: {str(e)}")
        return html_content

def generate_full_url(slug, page_type):
    """Generate full URL from slug and page type"""
    return f"{web_host.rstrip('/')}/{page_type}/{slug}"

def fetch_pages_by_type(page_type):
    all_pages = []
    page = 1
     
    while True:
        # Fetch data with pagination
        params = {
            'auth_token': auth_token,
            'page': page,
            'page_size': 100
        }
        
        url = f"{base_api_url}{page_type}/"
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch {page_type} pages. Status code: {response.status_code}")
            break
            
        data = response.json()
        pages = data['data']
        all_pages.extend(pages)
        
        # Check if there are more pages
        if not data['meta']['next_page']:
            break
            
        page += 1
    
    return all_pages

def save_links_file(all_pages):
    """Save links to a JSON file for LlamaIndex"""
    links = []
    for page, page_type in all_pages:
        slug = page.get('slug', '')
        url = generate_full_url(slug, page_type)
        links.append(url)
    
    with open('buttercms_links.json', 'w', encoding='utf-8') as f:
        json.dump({'links': links}, f, indent=2)
    
    print(f"Links file 'buttercms_links.json' created successfully with {len(links)} URLs.")

# Main execution
if __name__ == "__main__":
    page_types = ['documents', 'authors']
    all_pages = []
    
    # Fetch pages for each type
    for page_type in page_types:
        pages = fetch_pages_by_type(page_type)
        all_pages.extend([(page, page_type) for page in pages])
        print(f"Fetched {len(pages)} pages of type '{page_type}'")
    
    if all_pages:
        # Open a CSV file to write data
        with open('buttercms_pages.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'slug', 'url', 'cleaned_text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Iterate through each page data with progress bar
            for page, page_type in tqdm(all_pages, desc="Processing pages"):
                # Get page data
                title = page.get('fields', {}).get('title', '').strip()
                slug = page.get('slug', '')
                html_content = page.get('fields', {}).get('text', '')
                
                # Generate full URL
                url = generate_full_url(slug, page_type)
                
                # Clean the HTML content
                cleaned_text = clean_html_to_text(html_content)
                
                row = {
                    'title': title,
                    'slug': slug,
                    'url': url,
                    'cleaned_text': cleaned_text
                }
                
                writer.writerow(row)
        
        print(f"CSV file 'buttercms_pages.csv' created successfully with {len(all_pages)} total pages.")
        
        # Save links file
        # save_links_file(all_pages)
    else:
        print("No pages were fetched.")
