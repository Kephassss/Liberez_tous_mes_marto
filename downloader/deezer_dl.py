from .base import BaseDownloader
import os
import sys
from pathlib import Path

# Deemix imports
# We wrap them in try-except to avoid crashing if imports fail (though PyInstaller should bundle them)
try:
    from deezer import Deezer, TrackFormats
    from deemix import generateDownloadObject
    from deemix.settings import load as loadSettings
    # from deemix.utils import getBitrateNumberFromText, formatListener
    from deemix.downloader import Downloader
    from deemix.itemgen import GenerationError
    DEEMIX_AVAILABLE = True
except ImportError:
    DEEMIX_AVAILABLE = False

class LogListener:
    @classmethod
    def send(cls, key, value=None):
        # We can route this to our own logs if we want
        pass

class DeezerDownloader(BaseDownloader):
    def accept(self, query: str) -> bool:
        return "deezer.com" in query

    def download(self, query: str, output_path: str = ".", no_cover: bool = False) -> dict:
        if not DEEMIX_AVAILABLE:
            return {"status": "error", "message": "Deemix library not found. Please reinstall."}
            
        print(f"Downloading from Deezer via Library: {query}")
        
        # 1. Setup Config Paths
        if getattr(sys, 'frozen', False):
            project_root = Path(os.path.dirname(sys.executable))
        else:
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        config_folder = project_root / 'config' / 'deemix'
        config_folder.mkdir(parents=True, exist_ok=True)
        
        # 2. Setup ARL
        arl_file = config_folder / '.arl'
        arl = ""
        if arl_file.is_file():
            with open(arl_file, 'r', encoding="utf-8") as f:
                arl = f.readline().strip()
        
        dz = Deezer()
        if not arl or not dz.login_via_arl(arl):
            # Try to look for arl.txt in root (easier for user)
            simple_arl = project_root / 'arl.txt'
            if simple_arl.is_file():
                 with open(simple_arl, 'r', encoding="utf-8") as f:
                    arl = f.readline().strip()
            
            if not arl or not dz.login_via_arl(arl):
                return {
                    "status": "error", 
                    "message": "Deezer Login Failed. Please create an 'arl.txt' file with your ARL token next to the app."
                }
            
            # Save valid arl to config for future
            with open(arl_file, 'w', encoding="utf-8") as f:
                f.write(arl)
                
        # 3. Setup Settings
        settings = loadSettings(config_folder)
        settings['downloadLocation'] = output_path
        settings['tracknameTemplate'] = '%artist% - %title%'
        settings['albumTracknameTemplate'] = '%artist% - %title%'
        settings['playlistTracknameTemplate'] = '%artist% - %title%'
        settings['createSingleFolder'] = False # Don't create folder, we handle it? 
        # Actually Marto manager handles folders usually.
        # But deemix creates folders by default for albums/playlists.
        # We'll let deemix manage structure if it's an album?
        # User wants simple files usually.
        # Let's try to flatten it slightly if possible, or accept deemix structure.
        settings['createStructurePlaylist'] = False
        settings['createStructure'] = False # Dump files in output_path
        
        if no_cover:
            settings['saveAlbumArt'] = False
            settings['embeddedArtworkSize'] = 0 # Disable?
            # Deemix specific keys for cover might vary, but saveAlbumArt is likely one.
        
        # Force FLAC if available
        bitrate = TrackFormats.FLAC
        # settings['maxBitrate'] = ... logic in deemix uses passing bitrate to generateDownloadObject
        
        # 4. Process Download
        links = [query]
        downloadObjects = []
        listener = LogListener()
        plugins = {} # Spotify plugins etc, we skip for now
        
        for link in links:
            try:
                # generateDownloadObject(dz, link, bitrate, plugins, listener)
                # bitrate enum: MP3_128, MP3_320, FLAC
                obj = generateDownloadObject(dz, link, bitrate, plugins, listener)
                if isinstance(obj, list):
                    downloadObjects += obj
                else:
                    downloadObjects.append(obj)
            except Exception as e:
                print(f"Error generating object: {e}")
                return {"status": "error", "message": f"Invalid Deezer link or error: {str(e)}"}

        files_downloaded = []
        
        # 5. Start Download
        for obj in downloadObjects:
            try:
                # Downloader(dz, obj, settings, listener).start()
                # This is blocking? Yes, usually threads are used in GUI but here we can block.
                # start() executes download.
                downloader = Downloader(dz, obj, settings, listener)
                downloader.start()
                
                # Collect filenames?
                # Deemix doesn't return path easily. 
                # We assume success if no exception.
            except Exception as e:
                return {"status": "error", "message": f"Download failed: {str(e)}"}

        return {
            "status": "success", 
            "title": "Deezer Download", 
            "files": [] # We can't easily list files
        }
