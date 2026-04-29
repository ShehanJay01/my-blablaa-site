import requests
import os
import xml.etree.ElementTree as ET
import html
from datetime import datetime

# Base configurations
BASE_URL = "https://mooov.online"
SITEMAP_FILE = "sitemap.xml"

# API list (Popular movies loop එක ඇතුළේ හදමු)
API_CONFIG = [
    {"url": "https://stmap.mooov.online/movie/top_rated?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/tv/popular?language=en-US&page=1", "type": "tv"},
    {"url": "https://stmap.mooov.online/tv/top_rated?language=en-US&page=1", "type": "tv"}
]

def generate_sitemap():
    today = datetime.now().strftime('%Y-%m-%d')
    url_date_map = {}

    try:
        # 1. පවතින Sitemap එක කියවීම
        if os.path.exists(SITEMAP_FILE) and os.path.getsize(SITEMAP_FILE) > 0:
            try:
                tree = ET.parse(SITEMAP_FILE)
                root = tree.getroot()
                ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                for url_tag in root.findall('ns:url', ns):
                    loc_tag = url_tag.find('ns:loc', ns)
                    if loc_tag is not None:
                        loc = loc_tag.text
                        lastmod = url_tag.find('ns:lastmod', ns)
                        clean_url = html.unescape(loc)
                        url_date_map[clean_url] = lastmod.text if lastmod is not None else today
            except Exception as e:
                print(f"Old sitemap parse error: {e}")

        # Browser එකක් වගේ පෙනෙන්න Headers දාමු
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        homepage = f"{BASE_URL}/"
        if homepage not in url_date_map:
            url_date_map[homepage] = today

        # --- Popular Movies (Pages 1 to 4) ---
        for page in range(1, 5):
            url = f"https://stmap.mooov.online/movie/popular?language=en-US&page={page}"
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get('results', []):
                        item_id = item.get('id')
                        if item_id:
                            item_url = f"{BASE_URL}/movie?id={item_id}&type=movie"
                            if item_url not in url_date_map:
                                url_date_map[item_url] = today
                    print(f"Success: Popular Movies Page {page}")
                else:
                    print(f"Failed: Page {page} (Status: {res.status_code})")
            except Exception as e:
                print(f"Error fetching page {page}: {e}")

        # --- අනෙක් API (Top Rated & TV) ---
        for config in API_CONFIG:
            try:
                res = requests.get(config['url'], headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get('results', []):
                        item_id = item.get('id')
                        if item_id:
                            item_url = f"{BASE_URL}/{config['type']}?id={item_id}&type={config['type']}"
                            if item_url not in url_date_map:
                                url_date_map[item_url] = today
                    print(f"Success: {config['url']}")
                else:
                    print(f"Failed: {config['url']} (Status: {res.status_code})")
            except Exception as e:
                print(f"Error: {e}")

        # 3. XML ලිවීම
        content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for url in sorted(url_date_map.keys()):
            priority = "1.0" if url in [homepage, f"{BASE_URL}"] else "0.8"
            content += f'  <url>\n    <loc>{html.escape(url)}</loc>\n    <lastmod>{url_date_map[url]}</lastmod>\n    <priority>{priority}</priority>\n  </url>\n'
        content += '</urlset>'

        with open(SITEMAP_FILE, "w") as f:
            f.write(content)
        
        print(f"Done! Sitemap has {len(url_date_map)} URLs.")

    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    generate_sitemap()
