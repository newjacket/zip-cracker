#!/bin/bash
# ============================================================
# ZIP密码恢复工具 - APK构建脚本
# 适用于 Ubuntu/Debian/WSL
# 使用方法: bash build_apk.sh
# ============================================================

set -e

echo "=============================================="
echo "  ZIP密码恢复工具 - APK构建"
echo "=============================================="

# 1. 安装系统依赖
echo ""
echo "[1/5] 安装系统依赖..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-dev \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    zip \
    unzip \
    wget \
    curl \
    zlib1g-dev

# 2. 安装Python依赖
echo ""
echo "[2/5] 安装Python依赖..."
pip3 install --upgrade pip
pip3 install buildozer cython==0.29.33 kivy pyzipper

# 3. 安装Android SDK命令行工具（如果没有）
echo ""
echo "[3/5] 检查Android SDK..."
if [ ! -d "$HOME/.buildozer/android/platform/android-sdk" ]; then
    echo "  Buildozer会自动下载Android SDK，首次构建需要较长时间..."
fi

# 4. 设置Java环境
echo ""
echo "[4/5] 配置Java环境..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
echo "  JAVA_HOME=$JAVA_HOME"

# 5. 构建APK
echo ""
echo "[5/5] 开始构建APK（首次构建约需30-60分钟）..."
echo "  请耐心等待，期间会自动下载Android SDK/NDK..."
echo ""

cd "$(dirname "$0")"
buildozer android debug

echo ""
echo "=============================================="
echo "  ✅ 构建完成！"
echo "  APK文件位置: bin/目录下"
echo "  文件名类似: zipcracker-1.0-arm64-v8a_armeabi-v7a-debug.apk"
echo "=============================================="
echo ""
echo "安装到手机:"
echo "  adb install bin/zipcracker-1.0-arm64-v8a_armeabi-v7a-debug.apk"
echo ""
