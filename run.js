const API_URL = "https://long-feather-aa6a.shehanmadhusith1999.workers.dev";

// --- Global Search & Redirection Logic (for all pages with a search bar) ---
function performSearch() {
    const query = document.getElementById("searchInput").value.trim();
    const type = document.getElementById("type").value;
    if (query) {
        window.location.href = `search.html?query=${encodeURIComponent(query)}&category=${encodeURIComponent(type)}`;
    }
}

function handleSearchInput(event) {
    if (event.key === "Enter") {
        performSearch();
    }
    // Optional: If you want specific behavior when search input is cleared on the homepage,
    // you'd add logic here, but for redirection, it's less critical here.
    // For search.html: if search input is cleared, you might want to redirect to index.html
    // For index.html: if search input is cleared, you might want to ensure home content is visible.
    const currentPath = window.location.pathname;
    if (document.getElementById("searchInput").value.trim() === "") {
        if (currentPath.includes("search.html")) {
            window.location.href = 'index.html'; // Go back to homepage if search is cleared on search.html
        } else if (currentPath.includes("index.html")) {
            document.getElementById("homeContent").style.display = "block";
            document.getElementById("results").innerHTML = ""; // Clear any leftover search result display
            document.getElementById("results").style.display = "none";
        }
    }
}

// --- Functions primarily for index.html ---
async function loadHomePageContent() {
    const homeContent = document.getElementById("homeContent");
    const results = document.getElementById("results"); // This results div is hidden for homepage display

    homeContent.style.display = "block";
    results.innerHTML = "";
    results.style.display = "none"; // Ensure search results are hidden on homepage load

    try {
        await loadHeroSection();
        await fetchAndDisplayContent('movie', 'trending', 'trendingMovies');
        await fetchAndDisplayContent('movie', 'top_rated', 'topRatedMovies');
        await fetchAndDisplayContent('tv', 'trending', 'trendingTvShows');
        await fetchAndDisplayContent('tv', 'top_rated', 'topRatedTvShows');
    } catch (error) {
        console.error("Error loading home page content:", error);
    }
}

async function loadHeroSection() {
    const heroSection = document.getElementById('heroSection');
    if (!heroSection) return; // Ensure element exists on the page
    heroSection.innerHTML = '<p>Loading main feature...</p>';

    try {
        const response = await fetch(`${API_URL}/trending?type=movie`);
        if (!response.ok) throw new Error("Network response for hero section was not ok");
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            const movie = data.results[0];
            const posterUrl = (movie.backdrop_path && movie.backdrop_path.startsWith("http")) ? movie.backdrop_path : 'placeholder_backdrop.jpg';
            const thumbnailUrl = (movie.thumb && movie.thumb.startsWith("http")) ? movie.thumb : 'placeholder.jpg';

            heroSection.style.backgroundImage = `linear-gradient(to right, rgba(0,0,0,0.7), rgba(0,0,0,0.2)), url('${posterUrl}')`;
            heroSection.innerHTML = `
                <div class="hero-content">
                    <h1>${movie.name || movie.original_title || 'Untitled'}</h1>
                    <p>${movie.overview || 'No description available.'}</p>
                    <div class="hero-buttons">
                        <a href="movie.html?id=${encodeURIComponent(movie.id)}&type=movie" class="watch-trailer-btn">Watch Trailer</a>
                        <a href="movie.html?id=${encodeURIComponent(movie.id)}&type=movie" class="watch-now-btn">Watch Now</a>
                    </div>
                </div>
                <img src="${thumbnailUrl}" alt="${movie.name || movie.original_title || 'No title'}" class="hero-thumbnail">
            `;
            // Add inline styles for hero-thumbnail or move to CSS
            const heroThumbnail = heroSection.querySelector('.hero-thumbnail');
            if(heroThumbnail) {
                heroThumbnail.style.position = 'absolute';
                heroThumbnail.style.right = '5%';
                heroThumbnail.style.bottom = '10%';
                heroThumbnail.style.width = '250px';
                heroThumbnail.style.borderRadius = '10px';
                heroThumbnail.style.boxShadow = '0 8px 16px rgba(0,0,0,0.5)';
            }


        } else {
            heroSection.innerHTML = '<p>No main feature available.</p>';
        }
    } catch (error) {
        console.error("Error loading hero section:", error);
        heroSection.innerHTML = '<p>Error loading main feature. Please try again later.</p>';
    }
}

async function fetchAndDisplayContent(type, category, elementId) {
    const container = document.getElementById(elementId);
    if (!container) return; // Ensure element exists on the page
    container.innerHTML = "<p>Loading...</p>";

    try {
        const response = await fetch(`${API_URL}/${category}?type=${type}`);
        if (!response.ok) throw new Error(`Network response for ${category} ${type} was not ok`);
        const data = await response.json();

        if (!data.results || data.results.length === 0) {
            container.innerHTML = "<p>No content found.</p>";
            return;
        }

        container.innerHTML = "";

        data.results.forEach(item => {
            const div = document.createElement("div");
            div.className = "movie";

            const posterUrl = (item.thumb && item.thumb.startsWith("http")) ? item.thumb : 'placeholder.jpg';

            div.innerHTML = `
                <img src="${posterUrl}" alt="${item.name || item.original_title || 'No title'}" />
                <p>${item.name || item.original_title || "Untitled"}</p>
                <small>${item.release_date || item.first_air_date || ""}</small>
            `;

            div.onclick = () => {
                const id = item.id;
                window.location.href = `movie.html?id=${encodeURIComponent(id)}&type=${encodeURIComponent(type)}`;
            };

            container.appendChild(div);
        });

    } catch (error) {
        console.error(`Error loading ${category} ${type}:`, error);
        container.innerHTML = `<p>Error loading content. Please try again later.</p>`;
    }
}

// --- Functions primarily for search.html ---
async function searchMovies() {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('query');
    const type = urlParams.get('category'); // Using 'category' from URL for type

    const results = document.getElementById("results");
    const searchResultsTitle = document.getElementById("searchResultsTitle"); // Assuming you have this on search.html

    if (!results || !query) { // Ensure elements exist and query is present
        if (results) results.innerHTML = "<p>No search query provided.</p>";
        if (searchResultsTitle) searchResultsTitle.textContent = "No search query provided.";
        return;
    }

    results.innerHTML = "<p>Loading search results...</p>";
    if (searchResultsTitle) searchResultsTitle.textContent = `Search Results for "${query}" (${type || "All"}):`;
    // Ensure homeContent is not displayed if this is called on search.html
    const homeContent = document.getElementById("homeContent");
    if (homeContent) homeContent.style.display = "none";
    results.style.display = "grid"; // Make sure the results container is visible and styled as grid

    try {
        const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query)}&type=${encodeURIComponent(type || 'movie')}`); // Default to movie if type is missing

        if (!response.ok) throw new Error("Network response was not ok");

        const data = await response.json();

        if (!data.results || data.results.length === 0) {
            results.innerHTML = "<p>No results found.</p>";
            return;
        }

        results.innerHTML = "";

        data.results.forEach(item => {
            const div = document.createElement("div");
            div.className = "movie";

            const posterUrl = (item.thumb && item.thumb.startsWith("http")) ? item.thumb : 'placeholder.jpg';

            div.innerHTML = `
                <img src="${posterUrl}" alt="${item.name || item.original_title || 'No title'}" />
                <p>${item.name || item.original_title || "Untitled"}</p>
                <small>${item.release_date || item.first_air_date || ""}</small>
            `;

            div.onclick = () => {
                const id = item.id;
                window.location.href = `movie.html?id=${encodeURIComponent(id)}&type=${encodeURIComponent(type || 'movie')}`;
            };

            results.appendChild(div);
        });

    } catch (error) {
        results.innerHTML = `<p>Error loading results. Please try again later.</p>`;
        console.error("Search error:", error);
    }
}
