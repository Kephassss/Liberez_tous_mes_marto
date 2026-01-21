[app]
title = Marto
package.name = marto
package.domain = org.marto
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js,txt,json
version = 1.0

# Dependencies
requirements = python3,flask,requests,yt-dlp,mutagen,android,jnius

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android Specifics
android.api = 31
android.minapi = 21
android.archs = arm64-v8a

# Orientation
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
