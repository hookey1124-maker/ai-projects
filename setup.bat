@echo off
chcp 65001 >nul
echo ========================================
echo   AI项目 — 新电脑环境配置
echo ========================================
echo.

echo [1/7] 安装 Python 依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ pip install 失败，请检查 Python 是否已安装
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo [2/7] 安装 Playwright 浏览器...
playwright install chromium
if %errorlevel% neq 0 (
    echo ⚠️  Playwright 浏览器安装失败（不影响 Excel/OCR 功能）
)
echo ✅ Playwright 完成
echo.

echo [3/7] 修复硬编码路径（Administrator → 当前用户）...
REM 使用变量拼接旧用户名避免被 fix_paths.py 误替换
set "OLD_USER=Administrator"
set "OLD_PATH=C:/Users/%OLD_USER%/Desktop/AI项目"
set "NEW_PATH=%~dp0"
set "NEW_PATH=%NEW_PATH:\=/%"
if "%NEW_PATH:~-1%"=="/" set "NEW_PATH=%NEW_PATH:~0,-1%"
echo   旧路径: %OLD_PATH%
echo   新路径: %NEW_PATH%
powershell -Command "$oldUser='Administrator'; $oldPath='C:/Users/'+$oldUser+'/Desktop/AI项目'; $projectRoot='%NEW_PATH%'; Get-ChildItem -Path $projectRoot -Recurse -Include '*.json','*.py','*.md','*.bat' -File | Where-Object { $_.FullName -notmatch '\\node_modules\\|\\.venv\\|\\.git\\' } | ForEach-Object { $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue; if ($c -and $c.Contains($oldPath)) { $c = $c.Replace($oldPath, $projectRoot); [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false)); Write-Host ('  ✓ ' + $_.Name) } }"
echo ✅ 路径替换完成
echo.

echo [4/7] 安装 Git post-merge hook（每次 pull 自动修正路径）...
if not exist ".git\hooks\" mkdir ".git\hooks"
(
echo #!/bin/bash
echo # Auto-fix Administrator paths after each git pull
echo REPO_ROOT="$(git rev-parse --show-toplevel)"
echo SCRIPT="$REPO_ROOT/fix_paths.py"
echo if [ -f "$SCRIPT" ]; then
echo     echo "[post-merge] Running fix_paths.py..."
echo     python "$SCRIPT"
echo else
echo     echo "[post-merge] WARNING: fix_paths.py not found, skipping path fix."
echo fi
) > ".git\hooks\post-merge"
echo ✅ post-merge hook 安装完成
echo.

echo [5/7] 部署 Claude Code 配置...
if exist "%USERPROFILE%\.claude\.git" (
    echo ⚠️  .claude 已存在，跳过 clone
    cd /d "%USERPROFILE%\.claude"
    git pull
) else (
    git clone https://github.com/hookey1124-maker/claude-config.git "%USERPROFILE%\.claude"
)
if %errorlevel% neq 0 (
    echo ❌ Claude 配置 clone 失败，请检查网络和 git
) else (
    echo ✅ Claude 配置部署完成
)
echo.

echo [6/7] 安装 Node.js 依赖...
cd /d "%~dp0三部周报v1\New project 2-新品板块已放入"
if exist package.json (
    call npm install
    if %errorlevel% neq 0 (
        echo ⚠️  npm install 失败（不影响 Python 功能）
    ) else (
        echo ✅ Node 依赖安装完成
    )
) else (
    echo ⚠️  未找到 package.json，跳过
)
echo.

echo [7/7] 验证关键库...
python -c "import openpyxl; print('  openpyxl:', openpyxl.__version__)"
python -c "import pandas; print('  pandas:', pandas.__version__)"
python -c "import easyocr; print('  easyocr:', easyocr.__version__)"
python -c "import playwright; print('  playwright:', playwright.__version__)"
echo.

echo ========================================
echo   配置完成！
echo ========================================
echo.
echo ⚠️  请手动完成以下步骤：
echo   1. 编辑 agent升级计划\.mcp.json，替换 API 密钥：
echo      - GITHUB_TOKEN: YOUR_GITHUB_PAT_HERE → 真实 PAT
echo      - YOUR_ZHIPU_API_KEY → 智谱 API Key
echo      - YOUR_MAIZI_API_KEY → 麦子AI API Key
echo   2. VS Code Settings Sync 登录账号同步扩展
echo   3. 用 Claude Code 打开本项目即可开始工作
echo.
pause
