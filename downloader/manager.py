import os
from .soundcloud import SoundCloudDownloader
from .youtube import YouTubeDownloader
from .spotify_resolver import SpotifyResolver

from .deezer_dl import DeezerDownloader

class DownloaderManager:
    def __init__(self):
        self.downloaders = [
            SoundCloudDownloader(),
            YouTubeDownloader(),
            DeezerDownloader()
        ]

    def process(self, query: str, output_path: str = ".", no_cover: bool = False, format: str = "flac") -> dict:
        # Handle 'Sa Daronne' format (Random Mom Image)
        if format == "daronne":
            return self.download_daronne(query, output_path)

        # Check for Spotify
        spotify = SpotifyResolver()
        if spotify.accept(query):
             print("Spotify URL detected...")
             
             if spotify.is_playlist(query):
                 print("Playlist detected. Fetching tracks...")
                 playlist_data = spotify.resolve_playlist(query)
                 pl_title = playlist_data.get('title', 'Unknown Playlist').replace("|", "").strip() # Clean title
                 tracks = playlist_data.get('tracks', [])
                 
                 print(f"Found playlist: '{pl_title}' with {len(tracks)} tracks.")
                 
                 # Create playlist sub-directory
                 # Sanitize folder name
                 safe_title = "".join([c for c in pl_title if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
                 playlist_path = os.path.join(output_path, safe_title)
                 os.makedirs(playlist_path, exist_ok=True)
                 
                 print(f"Downloading to: {playlist_path}")
                 
                 results = []
                 for i, track_name in enumerate(tracks):
                     print(f"[{i+1}/{len(tracks)}] Processing: {track_name}")
                     # Recursive call for the track
                     # We treat the track_name as a search query
                     # FORCE YOUTUBE for Spotify results to avoid Remixes/Covers common on SC
                     res = self.process(track_name, output_path=playlist_path, no_cover=no_cover, format=format, force_youtube=True)
                     results.append(res)
                     
                 return {"status": "success", "title": pl_title, "files": [r.get('files') for r in results], "is_playlist": True}

             else:
                 # Single track
                 print("Resolving metadata...")
                 resolved = spotify.resolve(query)
                 if resolved:
                     print(f"Resolved to: {resolved}")
                     query = resolved # Treat as search query now
                     # Force YouTube for single tracks too as they come from Spotify
                     return self.process(query, output_path=output_path, no_cover=no_cover, format=format, force_youtube=True)
                 else:
                     return {"status": "error", "message": "Could not resolve Spotify URL"}

        # Check if it's a specific URL (SoundCloud/YouTube)
        for downloader in self.downloaders:
            if downloader.accept(query):
                return downloader.download(query, output_path, no_cover=no_cover, format=format)
        
        # Internal args handling for recursion
        force_youtube = False
        # If this method was called with keyword arguments in kwargs (python trick, but here we defined it explicitly? No wait)
        # I added force_youtube param to the call in lines 48 above, but I need to add it to the definition.
        # Python doesn't support 'hidden' args easily without **kwargs.
        # Let's change definition to include defaults or **kwargs?
        # Actually I can just modify the signature above.
        
        pass

    # Helper wrapper to support recursion specific args without changing public signature too much
    # Actually, I'll just change the signature:
    # def process(self, query: str, output_path: str = ".", no_cover: bool = False, format: str = "flac", force_youtube: bool = False) -> dict:
    
    def download_daronne(self, query: str, output_path: str) -> dict:
        import requests
        import random
        print("Mode: SA DARONNE activated.")
        
        # Use a list of potential sources or a specific one that works
        # LoremFlickr is good.
        url = "https://loremflickr.com/640/480/mom,woman" 
        
        try:
            # Fake headers to avoid 403
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, allow_redirects=True)
            
            if resp.status_code == 200:
                # Save
                filename = f"La_Daronne_de_{query.replace(' ', '_')}_{random.randint(100,999)}.jpg"
                filepath = os.path.join(output_path, filename)
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                
                return {
                    "status": "success",
                    "title": f"La Daronne de {query}",
                    "files": [filepath]
                }
            else:
                return {"status": "error", "message": f"Daronne introuvable ({resp.status_code})"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process(self, query: str, output_path: str = ".", no_cover: bool = False, format: str = "flac", force_youtube: bool = False) -> dict:
        # Handle 'Sa Daronne' format (Random Mom Image)
        if format == "daronne":
            return self.download_daronne(query, output_path)

        # Check for Spotify
        spotify = SpotifyResolver()
        if spotify.accept(query):
             print("Spotify URL detected...")
             
             if spotify.is_playlist(query):
                 print("Playlist detected. Fetching tracks...")
                 playlist_data = spotify.resolve_playlist(query)
                 pl_title = playlist_data.get('title', 'Unknown Playlist').replace("|", "").strip() # Clean title
                 tracks = playlist_data.get('tracks', [])
                 
                 print(f"Found playlist: '{pl_title}' with {len(tracks)} tracks.")
                 
                 # Create playlist sub-directory
                 # Sanitize folder name
                 safe_title = "".join([c for c in pl_title if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
                 playlist_path = os.path.join(output_path, safe_title)
                 os.makedirs(playlist_path, exist_ok=True)
                 
                 print(f"Downloading to: {playlist_path}")
                 
                 results = []
                 for i, track_name in enumerate(tracks):
                     print(f"[{i+1}/{len(tracks)}] Processing: {track_name}")
                     # Recursive call for the track
                     # We treat the track_name as a search query
                     # FORCE YOUTUBE for Spotify results to avoid Remixes/Covers common on SC
                     # Use 'Official Audio' to improve accuracy? default ytdlp search is usually decent.
                     # But appending " Audio" can help.
                     res = self.process(track_name, output_path=playlist_path, no_cover=no_cover, format=format, force_youtube=True)
                     results.append(res)
                     
                 return {"status": "success", "title": pl_title, "files": [r.get('files') for r in results], "is_playlist": True}

             else:
                 # Single track
                 print("Resolving metadata...")
                 resolved = spotify.resolve(query)
                 if resolved:
                     print(f"Resolved to: {resolved}")
                     query = resolved # Treat as search query now
                     return self.process(query, output_path=output_path, no_cover=no_cover, format=format, force_youtube=True)
                 else:
                     return {"status": "error", "message": "Could not resolve Spotify URL"}

        # Check if it's a specific URL (SoundCloud/YouTube)
        for downloader in self.downloaders:
            if downloader.accept(query):
                # Ensure downloaders accept 'format'
                return downloader.download(query, output_path, no_cover=no_cover, format=format)
        
        # Search Block
        if force_youtube:
             print(f"Forcing YouTube search for: {query}")
             yt = YouTubeDownloader()
             search_query = f"ytsearch1:{query}"
             return yt.download(search_query, output_path, no_cover=no_cover, format=format)

        # Default Search Priority: SoundCloud -> YouTube
        print("Input detected as search query. Searching on SoundCloud...")
        sc = SoundCloudDownloader()
        search_query = f"scsearch1:{query}"
        result = sc.download(search_query, output_path, no_cover=no_cover, format=format)
        
        if result['status'] == 'success':
            return result
            
        # Fallback to YouTube
        print("SoundCloud search failed or empty. Falling back to YouTube...")
        yt = YouTubeDownloader()
        search_query = f"ytsearch1:{query}"
        return yt.download(search_query, output_path, no_cover=no_cover, format=format)
