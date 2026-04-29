import requests
import os
import xml.etree.ElementTree as ET
import html
import time
from datetime import datetime

# Configurations
BASE_URL = "https://mooov.online"
WORKER_URL = "https://stmap.mooov.online" # ඔබේ Cloudflare Worker URL එක
SITEMAP_FILE = "sitemap.xml"

def generate_sitemap():
    today = datetime.now().strftime('%Y-%m-%d')
    url_date_map = {}

    # 1. පවතින Sitemap එක කියවීම
    if os.path.exists(SITEMAP_FILE) and os.path.getsize(SITEMAP_FILE) > 0:
        try:
            tree = ET.parse(SITEMAP_FILE)
            root = tree.getroot()
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for url_tag in root.findall('ns:url', ns):
                loc_node = url_tag.find('ns:loc', ns)
                if loc_node is not None:
                    loc = loc_node.text
                    lastmod = url_tag.find('ns:lastmod', ns)
                    url_date_map[html.unescape(loc)] = lastmod.text if lastmod is not None else today
        except Exception as e:
            print(f"පැරණි Sitemap කියවීමේ දෝෂයකි: {e}")

    # Browser එකක් ලෙස පෙනී සිටීමට Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://mooov.online/"
    }

    homepage = f"{BASE_URL}/"
    if homepage not in url_date_map:
        url_date_map[homepage] = today

    # ලබාගත යුතු ලිපිනයන් සකස් කිරීම
    endpoints = []
    # Popular Movies (Pages 1 to 4)
    for p in range(1, 5):
        endpoints.append({"url": f"{WORKER_URL}/movie/popular?language=en-US&page={p}", "type": "movie"})
    
    # Top Rated & TV
    endpoints.extend([
        {"url": f"{WORKER_URL}/movie/top_rated?language=en-US&page=1", "type": "movie"},
        {"url": f"{WORKER_URL}/tv/popular?language=en-US&page=1", "type": "tv"},
        {"url": f"{WORKER_URL}/tv/top_rated?language=en-US&page=1", "type": "tv"}
    ])

    print("දත්ත ලබා ගැනීම ආරම්භ කරනවා...")

    for ep in endpoints:
        try:
            # සෘජුවම Worker එකට request එක යැවීම
            response = requests.get(ep['url'], headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                for item in results:
                    item_id = item.get('id')
                    if item_id:
                        # වෙබ් අඩවියේ පෙන්වන ලින්ක් එක සැකසීම
                        item_url = f"{BASE_URL}/{ep['type']}?id={item_id}&type={ep['type']}"
                        if item_url not in url_date_map:
                            url_date_map[item_url] = today
                print(f"සාර්ථකයි: {ep['url']}")
            else:
                print(f"දෝෂයකි ({response.status_code}): {ep['url']}")
                print(f"පණිවිඩය: {response.text[:100]}")
            
            # Worker එකට සහ TMDB එකට අධික බරක් නොදීමට තත්පර 1ක් නවතින්න
            time.sleep(1)

        except Exception as e:
            print(f"Fetch failed for {ep['url']}: {e}")

    # 3. XML ගොනුව ලිවීම
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in sorted(url_date_map.keys()):
        priority = "1.0" if url == homepage else "0.8"
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{html.escape(url)}</loc>\n'
        sitemap_content += f'    <lastmod>{url_date_map[url]}</lastmod>\n'
        sitemap_content += f'    <priority>{priority}</priority>\n'
        sitemap_content += '  </url>\n'
    
    sitemap_content += '</urlset>'

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print(f"\nනිමයි! මුළු URLs ගණන: {len(url_date_map)}")

if __name__ == "__main__":
    generate_sitemap()
