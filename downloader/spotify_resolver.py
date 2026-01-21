import requests
from bs4 import BeautifulSoup

class SpotifyResolver:
    def accept(self, query: str) -> bool:
        return "open.spotify.com" in query

    def is_playlist(self, query: str) -> bool:
        return "playlist" in query

    def resolve_playlist(self, url: str) -> dict:
        """
        Resolves a Spotify playlist URL to a list of 'Artist - Title' strings.
        Returns: {'title': 'Playlist Name', 'tracks': ['Artist - Song', ...]}
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Get Playlist Title
                title_tag = soup.find('h1')
                playlist_title = title_tag.text.strip() if title_tag else "Unknown Playlist"
                
                # Extract Tracks
                # Spotify's public HTML structure changes often. 
                # Meta tags are usually reliable for at least some tracks.
                # Or looking for specific link patterns /track/
                
                tracks = []
                # Finding all links that look like tracks
                # Note: This scrapes the visible links. Infinite scroll might hide some on very long playlists,
                # but for a simple tool this covers the initial batch (usually 30-100).
                track_links = soup.find_all('a', href=True)
                
                seen_sub_urls = set()

                for link in track_links:
                    href = link['href']
                    if "/track/" in href:
                        # Avoid duplicates
                        if href in seen_sub_urls:
                            continue
                        seen_sub_urls.add(href)
                        
                        # We can either resolve each URL (slow) or try to find the text in the <a> tag or nearby
                        # Often the link text is the song name or parsing the title attribute.
                        
                        # Let's try to just collect the URLs and rely on our single-track resolver?
                        # Or resolving them here is better for batching.
                        full_url = "https://open.spotify.com" + href if href.startswith("/") else href
                        resolved_name = self.resolve(full_url)
                        if resolved_name:
                             tracks.append(resolved_name)

                return {
                    "title": playlist_title,
                    "tracks": tracks
                }
        except Exception as e:
            print(f"Error resolving Spotify Playlist: {e}")
        return {"title": "Error", "tracks": []}

    def resolve(self, url: str) -> str:
        """
        Fetches the Spotify page and extracts 'Track - Artist' from the title.
        This avoids needing API keys.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    # Title format is usually "Song - Artist | Spotify"
                    page_title = title_tag.text
                    clean_title = page_title.replace(" | Spotify", "")
                    return clean_title
        except Exception as e:
            print(f"Error resolving Spotify URL: {e}")
        return None
