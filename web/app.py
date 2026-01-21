from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent dir to path to import downloader.manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from downloader.manager import DownloaderManager

app = Flask(__name__)

# Handle Frozen state (PyInstaller)
if getattr(sys, 'frozen', False):
    # Running in a bundle
    template_folder = os.path.join(sys._MEIPASS, 'web', 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'web', 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    
    # Downloads next to the EXE
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(sys.executable), "downloads")
else:
    # Running normally
    app = Flask(__name__)
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads")

manager = DownloaderManager()

import tkinter as tk
from tkinter import filedialog
import threading

# Global to store current selection (in a real app per-session, but local tool global is fine)
current_output_dir = DEFAULT_OUTPUT_DIR

@app.route('/')
def index():
    return render_template('index.html', current_path=current_output_dir)

@app.route('/select_folder', methods=['POST'])
def select_folder():
    global current_output_dir
    # Tkinter needs to run in main thread usually, or at least be handled carefully.
    # We create a hidden root window.
    try:
        root = tk.Tk()
        root.withdraw() # Hide window
        root.attributes('-topmost', True) # Bring dialog to front
        folder_selected = filedialog.askdirectory()
        root.destroy()
        
        if folder_selected:
            current_output_dir = folder_selected
            return jsonify({"status": "success", "path": current_output_dir})
        else:
            return jsonify({"status": "cancelled", "path": current_output_dir})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/open_folder', methods=['POST'])
def open_folder():
    try:
        print(f"Opening folder: {current_output_dir}")
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)
            
        # Windows only startfile
        os.startfile(current_output_dir)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error opening folder: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

import random

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query')
    no_cover = data.get('no_cover', False)
    format = data.get('format', 'flac')
    
    if not query:
        return jsonify({"status": "error", "message": "No query provided"}), 400

    # Easter Eggs
    clean_query = query.lower().strip()
    if clean_query == "keketamine":
        print("Easter Egg Triggered: Keketamine -> Papaoutai")
        query = "Stromae - Papaoutai"
    elif clean_query == "titoun":
        print("Easter Egg Triggered: Titoun -> Arma Jackson BBL")
        query = "Arma Jackson - BBL"
    elif clean_query in ["lorenzo", "isidore"]:
        print(f"Easter Egg Triggered: {clean_query} -> Random Hardstyle/Techno")
        options = [
            "Tevvez - Legend",
            "Zyzz - Hardstyle",
            "Headhunterz - Destiny",
            "Showtek - FTS",
            "Ran-D - Zombie"
        ]
        query = random.choice(options)
    elif clean_query in ["bouingy", "fossil"]:
        print(f"Easter Egg Triggered: {clean_query} -> David Guetta")
        # Trying to find a "Best of" or playlist, but a search works
        query = "David Guetta Best Of 2024"
    elif clean_query == "darkshadow":
        print("Easter Egg Triggered: Darkshadow -> Random Drop")
        options = [
            "Darude - Sandstorm", 
            "Rick Astley - Never Gonna Give You Up",
            "Slayer - Raining Blood",
            "DragonForce - Through the Fire and Flames",
            "Nyan Cat Theme"
        ]
        query = random.choice(options)
        print(f"Random selection: {query}")

    try:
        # Use valid current_output_dir
        result = manager.process(query, output_path=current_output_dir, no_cover=no_cover, format=format)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- PLAYER / LIBRARY ROUTES ---
try:
    import library
except ImportError:
    from web import library
from flask import send_from_directory

@app.route('/api/library')
def get_library():
    """Returns the list of downloaded music"""
    try:
        current_path = current_output_dir
        tracks = library.scan_library(current_path)
        return jsonify({"status": "success", "tracks": tracks, "root": current_path})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stream/<path:filename>')
def stream_music(filename):
    """Streams an audio file from the current output dir"""
    try:
        return send_from_directory(current_output_dir, filename)
    except Exception as e:
        print(f"Stream error: {e}")
        return str(e), 404

@app.route('/download_file/<path:filename>')
def download_music_file(filename):
    """Forces download of the file"""
    try:
        return send_from_directory(current_output_dir, filename, as_attachment=True)
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    # host='0.0.0.0' is crucial for mobile access
    app.run(debug=True, port=5000, host='0.0.0.0')
