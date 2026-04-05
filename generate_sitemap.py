import requests
import os
import xml.etree.ElementTree as ET
import html

# API URLs 4ක් (Movies සහ TV Shows)
API_CONFIG = [
    {"url": "https://stmap.mooov.online/movie/popular?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/movie/top_rated?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/tv/popular?language=en-US&page=1", "type": "tv"},
    {"url": "https://stmap.mooov.online/tv/top_rated?language=en-US&page=1", "type": "tv"}
]

BASE_URL = "https://mooov.online"
SITEMAP_FILE = "sitemap.xml"

def generate_sitemap():
    try:
        existing_urls = set()
        # 1. පරණ එක කියවීමේදී සිදුවන XML Error එක මඟ හැරීම
        if os.path.exists(SITEMAP_FILE):
            try:
                tree = ET.parse(SITEMAP_FILE)
                root = tree.getroot()
                ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                for loc in root.findall('.//ns:loc', ns):
                    # පරණ URL එකේ & තිබුනොත් එය සාමාන්‍ය & බවට පත් කර ගබඩා කරයි
                    clean_url = html.unescape(loc.text)
                    existing_urls.add(clean_url)
            except Exception:
                print("Old sitemap had errors. Starting fresh.")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        existing_urls.add(f"{BASE_URL}/")

        # 2. API හරහා අලුත් දත්ත එකතු කිරීම
        for config in API_CONFIG:
            print(f"Fetching {config['type']} data from: {config['url']}")
            try:
                response = requests.get(config['url'], headers=headers)
                response.raise_for_status()
                data = response.json()
                results = data.get('results', [])
                
                for item in results:
                    item_id = item.get('id')
                    if item_id:
                        # වැදගත්: මෙතැනදී සාමාන්‍ය URL එක සාදයි
                        item_url = f"{BASE_URL}/{config['type']}?id={item_id}&type={config['type']}"
                        existing_urls.add(item_url)
            except Exception as api_error:
                print(f"Error fetching: {api_error}")

        print(f"Total unique URLs: {len(existing_urls)}")

        # 3. XML එක ලියන විට & ලකුණ &amp; බවට පත් කර ලිවීම
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in sorted(existing_urls):
            priority = "1.0" if url == f"{BASE_URL}/" or url == f"{BASE_URL}" else "0.8"
            # escape කිරීමෙන් & ලකුණ &amp; බවට පත්වේ
            safe_url = html.escape(url)
            sitemap_content += f'  <url>\n    <loc>{safe_url}</loc>\n    <priority>{priority}</priority>\n  </url>\n'
        
        sitemap_content += '</urlset>'

        with open(SITEMAP_FILE, "w") as f:
            f.write(sitemap_content)
        
        print("Sitemap successfully fixed and updated!")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    generate_sitemap()
