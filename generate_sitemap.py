import requests
import os

# ඔබේ අලුත් Worker URL එක මෙතනට නිවැරදිව ලබා දෙන්න
API_URL = "https://stmap.mooov.online/movie/popular?language=en-US&page=1"
BASE_URL = "https://mooov.online/movie"

def generate_sitemap():
    try:
        print(f"Fetching data from: {API_URL}")
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        print(f"Found {len(results)} movies.")

        if not results:
            print("No movies found! Sitemap will not be created.")
            return

        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap_content += f'  <url><loc>https://mooov.online/</loc><priority>1.0</priority></url>\n'

        for movie in results:
            movie_id = movie.get('id')
            url = f"{BASE_URL}?id={movie_id}&type=movie"
            sitemap_content += f'  <url><loc>{url}</loc><priority>0.8</priority></url>\n'
        
        sitemap_content += '</urlset>'
        
        # File එක write කිරීම
        with open("sitemap.xml", "w") as f:
            f.write(sitemap_content)
        
        # ඇත්තටම file එක හැදුනාද කියා check කිරීම
        if os.path.exists("sitemap.xml"):
            print("sitemap.xml created successfully in root directory!")
        else:
            print("Failed to create sitemap.xml file.")
            
    except Exception as e:
        print(f"Error during sitemap generation: {e}")

if __name__ == "__main__":
    generate_sitemap()
