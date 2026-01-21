from .base import BaseDownloader
import yt_dlp
import os
import imageio_ffmpeg

class YouTubeDownloader(BaseDownloader):
    def accept(self, query: str) -> bool:
        return "youtube.com" in query or "youtu.be" in query

    def download(self, query: str, output_path: str = ".", no_cover: bool = False, format: str = "flac") -> dict:
        print(f"Downloading from YouTube: {query}")
        
        # 1. Check if it's a playlist
        # SKIP if it's a search query (ytsearch...) because search results are technically playlists
        if not query.startswith("ytsearch"):
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl_peek:
                    info_peek = ydl_peek.extract_info(query, download=False, process=False)
                    
                    if info_peek and info_peek.get('_type') == 'playlist':
                        pl_title = info_peek.get('title', 'Unknown Playlist')
                        safe_title = "".join([c for c in pl_title if c.isalpha() or c.isdigit() or c in " .-_()"]).strip()
                        print(f"YouTube Playlist detected: '{pl_title}'. creating subfolder.")
                        output_path = os.path.join(output_path, safe_title)
            except Exception as e:
                 # Fallback to normal download if check fails (e.g. it's a search query 'ytsearch1:')
                 # ydl_peek might fail on search queries if process=False, usually it's fine.
                print(f"Debug: Playlist check skipped or failed: {e}")

        os.makedirs(output_path, exist_ok=True)
        
        # Post-processors config
        postprocessors = [
            {'key': 'FFmpegExtractAudio','preferredcodec': format},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
        ]
        if not no_cover:
             postprocessors.append({'key': 'EmbedThumbnail'})

        ydl_opts = {
            # Force Best Audio. If not available, fallback to video MAX 720p (avoiding 4k/8k 2GB files)
            'format': 'bestaudio/best[height<=720]',
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
                
                # Cleanup Thumbnails
                try:
                    base_name = info.get('title')
                    for img_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        thumb_path = os.path.join(output_path, f"{base_name}{img_ext}")
                        if os.path.exists(thumb_path):
                            os.remove(thumb_path)
                            print(f"Cleaned up thumbnail: {thumb_path}")
                except Exception as e:
                    print(f"Warning cleaning thumbnail: {e}")

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
