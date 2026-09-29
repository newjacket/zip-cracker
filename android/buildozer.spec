[app]

# 应用名称（显示在手机上）
title = ZIP密码恢复工具

# 包名
package.name = zipcracker

# 包域名（反向）
package.domain = org.example

# 源代码目录（包含main.py的目录）
source.dir = .

# 主程序入口
source.include_exts = py,png,jpg,kv,atlas

# 应用版本
version = 1.0

# 应用要求（权限）
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# Android API级别
android.api = 33

# Android NDK版本
android.ndk = 25b

# Android SDK版本
android.sdk = 24

# 最低Android版本
android.minapi = 21

# 目标Android版本
android.targetapi = 33

# 架构（armeabi-v7a, arm64-v8a, x86, x86_64）
android.archs = arm64-v8a, armeabi-v7a

# 全屏模式
android.fullscreen = 0

# 应用方向（portrait竖屏, landscape横屏, all自动）
android.orientation = portrait

# Python依赖（纯Python包）
requirements = python3, kivy, pyzipper

# 启动画面
# android.presplash_color = #FFFFFF

# 应用图标（替换为你的图标路径）
# icon.filename = %(source.dir)s/data/icon.png

# 启动画面
# presplash.filename = %(source.dir)s/data/presplash.png

# 允许写入外部存储
android.allow_backup = True

# 启用AndroidX
android.useAndroidX = True

[buildozer]

# 日志级别（0=error, 1=info, 2=debug）
log_level = 1

# 构建目录
build_dir = .buildozer

# 二进制目录
bin_dir = bin

# 警告级别
warn_on_root = 1

# 自动更新
android.accept_sdk_license = True
