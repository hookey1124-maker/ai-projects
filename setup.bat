@echo off
chcp 65001 >nul
echo ========================================
echo   AI项目 — 新电脑环境配置
echo ========================================
echo.

echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ pip install 失败，请检查 Python 是否已安装
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo [2/3] 安装 Playwright 浏览器...
playwright install chromium
if %errorlevel% neq 0 (
    echo ⚠️  Playwright 浏览器安装失败（不影响 Excel/OCR 功能）
)
echo ✅ Playwright 完成
echo.

echo [3/3] 验证关键库...
python -c "import openpyxl; print('  openpyxl:', openpyxl.__version__)"
python -c "import pandas; print('  pandas:', pandas.__version__)"
python -c "import easyocr; print('  easyocr:', easyocr.__version__)"
python -c "import playwright; print('  playwright:', playwright.__version__)"
echo.

echo ========================================
echo   配置完成！
echo   用 Claude Code 打开本项目即可开始工作
echo ========================================
pause
