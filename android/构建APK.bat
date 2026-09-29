@echo off
chcp 65001 >nul
echo ==============================================
echo   ZIP密码恢复工具 - APK构建（WSL方式）
echo ==============================================
echo.

REM 检查WSL是否安装
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到WSL，请先安装WSL2
    echo.
    echo 安装方法：以管理员身份打开PowerShell，执行：
    echo   wsl --install
    echo 安装完成后重启电脑，再运行此脚本
    pause
    exit /b 1
)

echo [1/3] 检查WSL发行版...
wsl --list --verbose
echo.

echo [2/3] 复制项目文件到WSL...
wsl bash -c "mkdir -p ~/zip_cracker && cp -r /mnt/c/Users/Administrator/Doubao/chats/zip_cracker/android/* ~/zip_cracker/ && echo 复制完成"
if %errorlevel% neq 0 (
    echo [错误] 文件复制失败
    pause
    exit /b 1
)
echo.

echo [3/3] 开始构建APK（首次约需30-60分钟）...
echo.
wsl bash -c "cd ~/zip_cracker && bash build_apk.sh"
if %errorlevel% neq 0 (
    echo.
    echo [错误] 构建失败，请查看上方错误信息
    pause
    exit /b 1
)

echo.
echo ==============================================
echo   构建完成！正在复制APK到桌面...
echo ==============================================
wsl bash -c "cp ~/zip_cracker/bin/*.apk /mnt/c/Users/Administrator/Desktop/ 2>/dev/null && echo APK已复制到桌面 || echo 未找到APK文件"
echo.
echo 请查看桌面是否有APK文件
pause
