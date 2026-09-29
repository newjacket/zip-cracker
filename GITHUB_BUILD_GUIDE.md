# GitHub Actions 在线构建APK指南

国内可正常访问GitHub，无需翻墙，完全免费。

## 操作步骤（约10分钟设置 + 30分钟自动构建）

### 第1步：注册/登录GitHub

1. 访问 https://github.com
2. 注册账号（如果没有）或登录

### 第2步：创建新仓库

1. 点击右上角 `+` → `New repository`
2. Repository name 填写：`zip-cracker`
3. 选择 `Public`（公开，免费版Actions可用）
4. 勾选 `Add a README file`
5. 点击 `Create repository`

### 第3步：上传代码

**方法A：网页上传（简单）**
1. 在仓库页面点击 `Add file` → `Upload files`
2. 把 `C:\Users\Administrator\Doubao\chats\zip_cracker\` 目录下的**所有文件和文件夹**拖进去
   - 包括：`android/` 文件夹、`.github/` 文件夹、`zip_cracker.py`、`README.md` 等
3. 点击 `Commit changes`

**方法B：用Git命令行（推荐）**
```bash
cd C:\Users\Administrator\Doubao\chats\zip_cracker
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/你的用户名/zip-cracker.git
git push -u origin main
```

### 第4步：触发构建

1. 上传完成后，点击仓库顶部的 `Actions` 标签
2. 你会看到 `Build Android APK` 工作流正在运行（黄色转圈）
3. 如果没有自动运行，点击 `Build Android APK` → `Run workflow` → 绿色按钮手动触发

### 第5步：等待构建完成

- 构建约需 **30-50分钟**
- 可以点击工作流名称查看实时日志
- 完成后状态会变成绿色 ✅

### 第6步：下载APK

1. 点击已完成的工作流（绿色对勾）
2. 页面最下方 `Artifacts` 区域
3. 点击 `zip-cracker-apk` 下载
4. 解压后得到APK文件

## ⚠️ 注意事项

1. **免费版限制**：GitHub Actions免费版每月有2000分钟额度，构建一次约用40分钟，完全够用
2. **构建超时**：工作流设置了120分钟超时，正常30-50分钟可完成
3. **首次构建**：会下载Android SDK/NDK，耗时较长
4. **仓库公开**：公开仓库才能免费使用Actions，代码会公开可见

## 常见问题

**Q: Actions页面显示空白？**
A: 首次需要在仓库 `Settings` → `Actions` → 选择 `Allow all actions`

**Q: 构建失败怎么办？**
A: 点击失败的工作流，查看红色错误信息，把错误发给我排查

**Q: 下载的是zip不是apk？**
A: 是的，GitHub把APK打包成zip了，解压后里面就是APK文件
