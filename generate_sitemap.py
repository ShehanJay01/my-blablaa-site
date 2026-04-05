import requests
import os

API_URL = "https://stmap.mooov.online/movie/popular?language=en-US&page=1"
BASE_URL = "https://mooov.online/movie"

def generate_sitemap():
    try:
        # මෙන්න මේ headers ටික අනිවාර්යයෙන්ම එකතු කරන්න
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        print(f"Fetching data from: {API_URL}")
        response = requests.get(API_URL, headers=headers) # headers මෙතනට දුන්නා
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        print(f"Found {len(results)} movies.")

        if not results:
            print("No movies found!")
            return

        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap_content += f'  <url><loc>https://mooov.online/</loc><priority>1.0</priority></url>\n'

        for movie in results:
            movie_id = movie.get('id')
            url = f"{BASE_URL}?id={movie_id}&type=movie"
            sitemap_content += f'  <url><loc>{url}</loc><priority>0.8</priority></url>\n'
        
        sitemap_content += '</urlset>'
        
        with open("sitemap.xml", "w") as f:
            f.write(sitemap_content)
        
        if os.path.exists("sitemap.xml"):
            print("sitemap.xml created successfully!")
            
    except Exception as e:
        print(f"Error during sitemap generation: {e}")

if __name__ == "__main__":
    generate_sitemap()
