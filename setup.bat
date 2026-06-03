@echo off
chcp 65001 >nul
echo ========================================
echo   AI项目 — 新电脑环境配置
echo ========================================
echo.

echo [1/5] 安装 Python 依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ pip install 失败，请检查 Python 是否已安装
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo [2/5] 安装 Playwright 浏览器...
playwright install chromium
if %errorlevel% neq 0 (
    echo ⚠️  Playwright 浏览器安装失败（不影响 Excel/OCR 功能）
)
echo ✅ Playwright 完成
echo.

echo [3/5] 部署 Claude Code 配置...
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

echo [4/5] 安装 Node.js 依赖...
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

echo [5/5] 验证关键库...
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
