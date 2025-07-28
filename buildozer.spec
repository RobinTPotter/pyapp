[app]
title = AndroidCameraApp
package.name = androidcameratest
package.domain = org.example
source.dir = .
source.include_exts = py
version = 0.1
requirements = python3,kivy,pyjnius
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.minapi = 21
android.target = 33
android.api = 33
android.useandroidx = True
entrypoint = main.py
orientation = portrait
fullscreen = 0
android.archs = armeabi-v7a,arm64-v8a
android.ndk_api = 21
log_level = 2

[buildozer]
