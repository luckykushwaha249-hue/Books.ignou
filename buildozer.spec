[app]

# App ka naam (phone pe yahi dikhega)
title = Books.IGNOU

# Package identity
package.name = booksapp
package.domain = org.ignou

# Source
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json
version = 1.0

# Requirements - poori app offline hai, koi extra network library nahi
requirements = python3,kivy==2.3.0,kivymd==1.1.1,plyer,pyjnius

# Orientation
orientation = portrait
fullscreen = 0

# Icon (chaho to apna icon.png isi folder me daal ke yeh line uncomment kar do)
# icon.filename = %(source.dir)s/icon.png

[android]

# Permissions - file upload/open (Storage Access Framework) ke liye
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# API levels
android.api = 33
android.minapi = 24
android.ndk_api = 24

# Architectures - zyada tar phones ke liye
android.archs = arm64-v8a,armeabi-v7a

# Backup allow
android.allow_backup = True

# AndroidX zaroori hai KivyMD ke liye
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
