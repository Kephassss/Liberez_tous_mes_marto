import os
import sys
import threading
import time
from web.app import app

# Kivy Imports through jnius/android
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False

def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

def start_android_webview():
    if not ANDROID:
        return
        
    # Request Permissions
    request_permissions([
        Permission.INTERNET, 
        Permission.WRITE_EXTERNAL_STORAGE, 
        Permission.READ_EXTERNAL_STORAGE
    ])
    
    # Wait for server to start
    time.sleep(2)
    
    # Open URL in default browser (Chrome) which gives PWA experience
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    
    intent = Intent(Intent.ACTION_VIEW)
    intent.setData(Uri.parse('http://localhost:5000'))
    PythonActivity.mActivity.startActivity(intent)

if __name__ == '__main__':
    # Start Flask in thread
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    if ANDROID:
        start_android_webview()
        # Keep main thread alive
        while True:
            time.sleep(1)
    else:
        # Desktop mode (testing)
        import webbrowser
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:5000')
        while True:
            time.sleep(1)