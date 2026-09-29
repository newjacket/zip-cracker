[app]
title = ZIP密码恢复工具
package.name = zipcracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25b
android.minapi = 21
android.targetapi = 33
android.archs = arm64-v8a, armeabi-v7a
android.fullscreen = 0
android.orientation = portrait
requirements = python3, kivy
android.allow_backup = True
android.useAndroidX = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
build_dir = .buildozer
bin_dir = bin
warn_on_root = 1
