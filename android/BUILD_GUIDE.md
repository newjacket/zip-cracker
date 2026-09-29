# ZIP密码恢复工具 - Android APK 构建指南

## 📱 应用功能

- 图形化界面（Kivy），支持触摸操作
- 掩码攻击（推荐，效率最高）
- 字符集暴力破解（短密码）
- 实时进度显示
- 支持AES加密和传统ZipCrypto加密的ZIP文件

## 🚀 三种构建方式

### 方式一：WSL2（Windows用户推荐）

#### 1. 安装WSL2

以管理员身份打开PowerShell：
```powershell
wsl --install
```
安装完成后重启电脑，设置Ubuntu用户名和密码。

#### 2. 在WSL中构建

打开Ubuntu终端，执行：
```bash
# 进入项目目录（Windows的C盘在WSL中是 /mnt/c/）
cd /mnt/c/Users/Administrator/Doubao/chats/zip_cracker/android

# 运行构建脚本
bash build_apk.sh
```

首次构建约需30-60分钟（自动下载Android SDK/NDK）。

#### 3. 获取APK

构建完成后，APK在 `bin/` 目录下：
```bash
ls bin/*.apk
```

将APK复制到Windows：
```bash
cp bin/*.apk /mnt/c/Users/Administrator/Desktop/
```

---

### 方式二：Google Colab（在线构建，无需本地环境）

打开 [Google Colab](https://colab.research.google.com/)，新建笔记本，执行：

```python
# 1. 安装依赖
!apt-get update -qq
!apt-get install -y -qq build-essential git python3 python3-pip openjdk-17-jdk autoconf libtool pkg-config cmake zip unzip wget
!pip install -q buildozer cython==0.29.33

# 2. 上传项目文件
# 点击左侧文件图标，上传 android/ 目录下的 main.py 和 buildozer.spec

# 3. 构建
!cd /content && buildozer android debug

# 4. 下载APK
from google.colab import files
import glob
apk_files = glob.glob('/content/bin/*.apk')
if apk_files:
    files.download(apk_files[0])
```

> 注意：Colab构建可能需要2-3小时，且可能因资源限制中断。

---

### 方式三：原生Linux（Ubuntu/Debian）

```bash
# 克隆或复制项目到Linux
cd /path/to/zip_cracker/android

# 运行构建脚本
bash build_apk.sh
```

---

## 📦 手动构建步骤（如果脚本失败）

```bash
# 1. 安装依赖
sudo apt install build-essential git python3-pip openjdk-17-jdk autoconf libtool cmake zip unzip
pip3 install buildozer cython==0.29.33

# 2. 设置Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# 3. 构建
cd android/
buildozer android debug

# 4. APK在 bin/ 目录
ls bin/
```

## 📲 安装到手机

### 方法一：ADB安装
```bash
# 手机开启USB调试，连接电脑
adb install bin/zipcracker-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

### 方法二：直接传输
1. 将APK文件复制到手机
2. 手机上点击APK文件安装
3. 首次安装需要允许"未知来源应用"

## ⚙️ 配置修改

编辑 `buildozer.spec` 可自定义：

| 配置项 | 说明 |
|--------|------|
| `title` | 应用名称 |
| `package.name` | 包名 |
| `version` | 版本号 |
| `android.archs` | CPU架构（arm64-v8a为现代手机） |
| `android.api` | Android API级别 |
| `requirements` | Python依赖包 |
| `icon.filename` | 应用图标路径 |

## 🎯 使用说明

1. 打开APP，输入压缩包完整路径（如 `/sdcard/Download/secret.zip`）
2. 选择攻击模式：
   - **掩码攻击**：输入掩码，如 `pass?d?d?d?d` 表示pass+4位数字
   - **暴力破解**：选择字符集和密码长度范围
3. 点击"开始破解"
4. 破解成功后密码会显示在结果区

### 掩码规则

| 符号 | 含义 | 字符数 |
|------|------|--------|
| `?d` | 数字 0-9 | 10 |
| `?l` | 小写字母 a-z | 26 |
| `?u` | 大写字母 A-Z | 26 |
| `?s` | 特殊符号 | 32 |
| `?a` | 全部可打印字符 | 94 |
| 其他 | 固定字符 | 1 |

## ⚠️ 注意事项

1. **性能限制**：手机CPU性能远低于电脑，破解速度约为电脑的1/5-1/10
2. **存储权限**：首次使用需要授予存储权限，才能读取压缩包文件
3. **Android 11+**：需要授予"所有文件访问权限"
4. **电池优化**：长时间破解建议连接充电器，并关闭电池优化
5. **合法用途**：仅用于恢复自己的压缩包密码

## 🔧 常见问题

**Q: 构建报错 `SDK license not accepted`**
A: 执行 `yes | sdkmanager --licenses` 接受所有许可

**Q: 构建报错 `Java not found`**
A: 确保安装了OpenJDK 17，并设置了JAVA_HOME

**Q: APK安装后闪退**
A: 检查logcat日志：`adb logcat | grep python`

**Q: 找不到压缩包文件**
A: Android 11+需要在设置中手动授予"所有文件访问权限"

## 📊 性能参考（手机端）

| 密码类型 | 组合数 | 预计时间 |
|----------|--------|----------|
| 4位数字 | 10,000 | ~5秒 |
| 6位数字 | 1,000,000 | ~10分钟 |
| 4位字母+数字 | 14,776,336 | ~2小时 |
| 6位字母+数字 | 2,176,782,336 | ~15天 |

> 复杂密码建议在电脑端使用字典攻击，手机端适合短密码或掩码攻击。
