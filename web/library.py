import os
import json

AUDIO_EXTENSIONS = ('.mp3', '.flac', '.wav', '.m4a', '.ogg')

def scan_library(root_path):
    """
    Scans the root_path for audio files.
    Returns a list of dicts:
    {
        'path': relative_path,
        'filename': filename,
        'folder': folder_name
    }
    """
    library = []
    
    if not os.path.exists(root_path):
        return []

    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(AUDIO_EXTENSIONS):
                full_path = os.path.join(root, file)
                # Get path relative to the downloads folder
                rel_path = os.path.relpath(full_path, root_path)
                
                # Simple metadata from filename
                folder_name = os.path.basename(root)
                if folder_name == os.path.basename(root_path):
                    folder_name = "Singles" # Root level files
                    
                library.append({
                    'path': rel_path.replace('\\', '/'), # Web friendly paths
                    'filename': file,
                    'title': os.path.splitext(file)[0],
                    'folder': folder_name
                })
                
    # Sort by folder then filename
    library.sort(key=lambda x: (x['folder'], x['title']))
    return library
