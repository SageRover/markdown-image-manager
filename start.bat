@echo off
title Markdown Image Manager
chcp 65001 >nul 2>&1
cls
echo ========================================
echo    Markdown Image Manager
echo ========================================
echo.
echo Starting application...
echo.
python markdown_image_manager.py
if %errorlevel% neq 0 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
) else (
    echo.
    echo Application closed normally.
    timeout /t 3 >nul
)