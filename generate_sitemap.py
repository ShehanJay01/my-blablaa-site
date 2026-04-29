import requests
import os
import xml.etree.ElementTree as ET
import html
import time
from datetime import datetime

# Configurations
BASE_URL = "https://mooov.online"
SITEMAP_FILE = "sitemap.xml"

# අනෙකුත් API සඳහා Configurations (Popular Movies හැර)
API_CONFIGS = [
    {"url": "https://stmap.mooov.online/movie/top_rated?language=en-US&page=1", "type": "movie"},
    {"url": "https://stmap.mooov.online/tv/popular?language=en-US&page=1", "type": "tv"},
    {"url": "https://stmap.mooov.online/tv/top_rated?language=en-US&page=1", "type": "tv"}
]

def generate_sitemap():
    today = datetime.now().strftime('%Y-%m-%d')
    url_date_map = {}

    # 1. පවතින Sitemap එක කියවා පැරණි දත්ත ආරක්ෂා කර ගැනීම
    if os.path.exists(SITEMAP_FILE) and os.path.getsize(SITEMAP_FILE) > 0:
        try:
            tree = ET.parse(SITEMAP_FILE)
            root = tree.getroot()
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for url_tag in root.findall('ns:url', ns):
                loc = url_tag.find('ns:loc', ns).text
                lastmod = url_tag.find('ns:lastmod', ns)
                url_date_map[html.unescape(loc)] = lastmod.text if lastmod is not None else today
        except Exception as e:
            print(f"පැරණි Sitemap එක කියවීමේ දෝෂයක්: {e}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Homepage එක එකතු කිරීම
    homepage = f"{BASE_URL}/"
    if homepage not in url_date_map:
        url_date_map[homepage] = today

    # 2. Popular Movies (Pages 1-4) ලබා ගැනීම
    for page in range(1, 5):
        pop_url = f"https://stmap.mooov.online/movie/popular?language=en-US&page={page}"
        try:
            response = requests.get(pop_url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    m_id = item.get('id')
                    if m_id:
                        link = f"{BASE_URL}/movie?id={m_id}&type=movie"
                        if link not in url_date_map:
                            url_date_map[link] = today
                print(f"Popular Movies Page {page} සාර්ථකයි.")
            else:
                print(f"Popular Movies Page {page} අසාර්ථකයි (Status: {response.status_code})")
            
            # API එකට විවේකයක් ලබා දීමට තත්පර 1ක් නවත්වන්න (Rate limit නොවීමට)
            time.sleep(1)
            
        except Exception as e:
            print(f"Page {page} ලබා ගැනීමේදී දෝෂයක්: {e}")

    # 3. අනෙකුත් API දත්ත ලබා ගැනීම
    for config in API_CONFIGS:
        try:
            response = requests.get(config['url'], headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    i_id = item.get('id')
                    if i_id:
                        link = f"{BASE_URL}/{config['type']}?id={i_id}&type={config['type']}"
                        if link not in url_date_map:
                            url_date_map[link] = today
                print(f"සාර්ථකයි: {config['url']}")
            time.sleep(1)
        except Exception as e:
            print(f"දෝෂයක් ({config['url']}): {e}")

    # 4. XML ගොනුව නිර්මාණය කිරීම
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in sorted(url_date_map.keys()):
        priority = "1.0" if url in [homepage, f"{BASE_URL}"] else "0.8"
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{html.escape(url)}</loc>\n'
        sitemap_content += f'    <lastmod>{url_date_map[url]}</lastmod>\n'
        sitemap_content += f'    <priority>{priority}</priority>\n'
        sitemap_content += '  </url>\n'
    
    sitemap_content += '</urlset>'

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print(f"\nSitemap එක සාර්ථකව නිම කළා! මුළු URL ගණන: {len(url_date_map)}")

if __name__ == "__main__":
    generate_sitemap()
