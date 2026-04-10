import requests
import os
import re
import xml.etree.ElementTree as ET
import html
from datetime import datetime

# API URLs
API_CONFIG = [
    {"url": "https://stmap.mooov.online/movie/popular?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/movie/top_rated?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/tv/popular?language=en-US&page=1", "type": "tv"},
    {"url": "https://stmap.mooov.online/tv/top_rated?language=en-US&page=1", "type": "tv"}
]

BASE_URL = "https://mooov.online"
SITEMAP_FILE = "sitemap.xml"

def generate_sitemap():
    today = datetime.now().strftime('%Y-%m-%d')
    url_date_map = {} # URL

    try:
        # 1. Read existing sitemap but skip old-format URLs (without title)
        if os.path.exists(SITEMAP_FILE):
            try:
                tree = ET.parse(SITEMAP_FILE)
                root = tree.getroot()
                ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                for url_tag in root.findall('ns:url', ns):
                    loc = url_tag.find('ns:loc', ns).text
                    lastmod = url_tag.find('ns:lastmod', ns)
                    
                    clean_url = html.unescape(loc)
                    # Skip old-format URLs that don't have 'title=' parameter
                    if 'movie?id=' in clean_url and 'title=' not in clean_url:
                        print(f"Skipping old-format URL: {clean_url}")
                        continue
                    # 
                    if lastmod is not None:
                        url_date_map[clean_url] = lastmod.text
                    else:
                        url_date_map[clean_url] = today
            except Exception as e:
                print(f"Error parsing old sitemap: {e}")

        # 2. 
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        
        # Homepage 
        homepage = f"{BASE_URL}/"
        if homepage not in url_date_map:
            url_date_map[homepage] = today

        for config in API_CONFIG:
            try:
                response = requests.get(config['url'], headers=headers)
                response.raise_for_status()
                data = response.json()
                results = data.get('results', [])
                for item in results:
                    item_id = item.get('id')
                    if item_id:
                        title = item.get('title') or item.get('name') or 'Unknown'
                        seo_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                        item_url = f"{BASE_URL}/movie?title={seo_title}&id={item_id}&type={config['type']}"
                        # URL
                        if item_url not in url_date_map:
                            url_date_map[item_url] = today
            except Exception as e:
                print(f"Fetch error: {e}")

        # 3. XML 
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in sorted(url_date_map.keys()):
            priority = "1.0" if url == homepage or url == f"{BASE_URL}" else "0.8"
            safe_url = html.escape(url)
            m_date = url_date_map[url]
            
            sitemap_content += '  <url>\n'
            sitemap_content += f'    <loc>{safe_url}</loc>\n'
            sitemap_content += f'    <lastmod>{m_date}</lastmod>\n'
            sitemap_content += f'    <priority>{priority}</priority>\n'
            sitemap_content += '  </url>\n'
        
        sitemap_content += '</urlset>'

        with open(SITEMAP_FILE, "w") as f:
            f.write(sitemap_content)
        
        print("Sitemap merged with historical dates successfully!")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    generate_sitemap()
