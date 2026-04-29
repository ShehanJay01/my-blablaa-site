import requests
import os
import xml.etree.ElementTree as ET
import html
from datetime import datetime

# Base configurations
BASE_URL = "https://mooov.online"
SITEMAP_FILE = "sitemap.xml"

# Popular movies 
API_CONFIG = [
    {"url": "https://stmap.mooov.online/movie/top_rated?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/tv/popular?language=en-US&page=1", "type": "tv"},
    {"url": "https://stmap.mooov.online/tv/top_rated?language=en-US&page=1", "type": "tv"}
]

def generate_sitemap():
    today = datetime.now().strftime('%Y-%m-%d')
    url_date_map = {}

    try:
        # 1. 
        if os.path.exists(SITEMAP_FILE):
            try:
                tree = ET.parse(SITEMAP_FILE)
                root = tree.getroot()
                ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                for url_tag in root.findall('ns:url', ns):
                    loc = url_tag.find('ns:loc', ns).text
                    lastmod = url_tag.find('ns:lastmod', ns)
                    clean_url = html.unescape(loc)
                    url_date_map[clean_url] = lastmod.text if lastmod is not None else today
            except Exception as e:
                print(f"Error parsing old sitemap: {e}")

        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        homepage = f"{BASE_URL}/"
        if homepage not in url_date_map:
            url_date_map[homepage] = today

        # --- Popular Movies 
        for page in range(1, 5): # 
            popular_url = f"https://stmap.mooov.online/movie/popular?language=en-US&page={page}"
            try:
                response = requests.get(popular_url, headers=headers)
                data = response.json()
                for item in data.get('results', []):
                    item_id = item.get('id')
                    if item_id:
                        item_url = f"{BASE_URL}/movie?id={item_id}&type=movie"
                        if item_url not in url_date_map:
                            url_date_map[item_url] = today
                print(f"Fetched Popular Movies: Page {page}")
            except Exception as e:
                print(f"Error fetching popular movie page {page}: {e}")

        # --- 
        for config in API_CONFIG:
            try:
                response = requests.get(config['url'], headers=headers)
                data = response.json()
                for item in data.get('results', []):
                    item_id = item.get('id')
                    if item_id:
                        item_url = f"{BASE_URL}/{config['type']}?id={item_id}&type={config['type']}"
                        if item_url not in url_date_map:
                            url_date_map[item_url] = today
            except Exception as e:
                print(f"Fetch error for {config['url']}: {e}")

        # 3. XML 
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in sorted(url_date_map.keys()):
            priority = "1.0" if url == homepage or url == f"{BASE_URL}" else "0.8"
            sitemap_content += '  <url>\n'
            sitemap_content += f'    <loc>{html.escape(url)}</loc>\n'
            sitemap_content += f'    <lastmod>{url_date_map[url]}</lastmod>\n'
            sitemap_content += f'    <priority>{priority}</priority>\n'
            sitemap_content += '  </url>\n'
        
        sitemap_content += '</urlset>'

        with open(SITEMAP_FILE, "w") as f:
            f.write(sitemap_content)
        
        print(f"Sitemap updated successfully with {len(url_date_map)} URLs!")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    generate_sitemap()
