from .base import BaseDownloader
import yt_dlp
import os
import imageio_ffmpeg

class SoundCloudDownloader(BaseDownloader):
    def accept(self, query: str) -> bool:
        # Simple check for soundcloud URL
        return "soundcloud.com" in query

    def download(self, query: str, output_path: str = ".", no_cover: bool = False, format: str = "flac") -> dict:
        print(f"Downloading from SoundCloud: {query}")
        
        # 1. Check if it's a playlist/set first (Fast check)
        # We need to peek at metadata without downloading
        # SKIP if it's a search query (scsearch...) because search results are technically playlists
        if not query.startswith("scsearch"):
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl_peek:
                    info_peek = ydl_peek.extract_info(query, download=False, process=False)
                    
                    # Check for playlist
                    # Note: process=False returns a generator for entries sometimes, or dict.
                    # If _type is playlist, update path.
                    if info_peek and info_peek.get('_type') == 'playlist':
                        pl_title = info_peek.get('title', 'Unknown Playlist')
                        # Sanitize
                        safe_title = "".join([c for c in pl_title if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
                        print(f"SoundCloud Playlist detected: '{pl_title}'. creating subfolder.")
                        output_path = os.path.join(output_path, safe_title)

            except Exception as e:
                print(f"Warning checking playlist status: {e}")

        # Ensure output directory exists (updated or original)
        os.makedirs(output_path, exist_ok=True)
        
        # Post-processors config
        postprocessors = [
            {'key': 'FFmpegExtractAudio','preferredcodec': format},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
        ]
        
        if not no_cover:
             postprocessors.append({'key': 'EmbedThumbnail'})

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
            'writethumbnail': not no_cover,
            'addmetadata': True,
            'postprocessors': postprocessors,
            'quiet': False,
            'no_warnings': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                
                # Handle search results (playlist)
                if 'entries' in info:
                    if not info['entries']:
                         return {"status": "error", "message": "No results found"}
                    # For search results, we usually just want the first one
                    # But yt-dlp might have downloaded all if we didn't limit?
                    # scsearch1: limits to 1.
                    info = info['entries'][0]

                filename = info.get('title') # Fallback
                
                # Cleanup Thumbnails
                # yt-dlp leaves the thumbnail file even if embedded. We delete it manually.
                # Sanitize title for filename matching roughly (yt-dlp sanitization might vary, but we catch standard ones)
                # Safer: list dir and check for files starting with the title and ending in image ext
                
                try:
                    import glob
                    # We need to handle potential sanitization in filenames. 
                    # But simplified: look for files in output_path
                    # We use the title we extracted.
                    
                    # Note: filenames might differ if yt-dlp sanitized characters.
                    # Best effort: Use info['requested_downloads'][0]['filepath'] to guess? 
                    # Or just wildcard matching based on title prefix if unique enough.
                    
                    # Let's iterate over common image extensions
                    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                         # Careful not to delete other songs.
                         # We can assume the filename starts with the title.
                         # But checking exact match is hard without sanitization func.
                         # Let's try to find files that match the base name of the downloaded file?
                         pass
                         
                    # Revised approach: 
                    # We know the output template is '%(title)s.%(ext)s'
                    # So the thumbnail should be 'Title.jpg' etc.
                    # We just try to delete them.
                    
                    base_name = info.get('title')
                    # Sanitize strictly if needed, but for now try direct
                    for img_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        thumb_path = os.path.join(output_path, f"{base_name}{img_ext}")
                        if os.path.exists(thumb_path):
                            os.remove(thumb_path)
                            print(f"Cleaned up thumbnail: {thumb_path}")
                            
                except Exception as cleanup_err:
                    print(f"Warning: Could not cleanup thumbnail: {cleanup_err}")

                return {
                    "status": "success",
                    "title": info.get('title'),
                    "files": [os.path.join(output_path, f"{info.get('title')}.{format}")] 
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
