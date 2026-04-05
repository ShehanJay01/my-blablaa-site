import requests

# 
API_URL = "https://stmap.mooov.online/movie/popular?language=en-US&page=1"
BASE_URL = "https://mooov.online/movie"

def generate_sitemap():
    try:
        # 
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        sitemap_content += f'  <url>\n    <loc>https://mooov.online/</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'

        for movie in data.get('results', []):
            movie_id = movie.get('id')
            if movie_id:
                url = f"{BASE_URL}?id={movie_id}&type=movie"
                sitemap_content += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
        
        sitemap_content += '</urlset>'
        
        with open("sitemap.xml", "w") as f:
            f.write(sitemap_content)
            
        print("Sitemap generated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_sitemap()
