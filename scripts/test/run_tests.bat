@echo off
chcp 65001 >nul
title CAE-CLI 测试运行器

echo ========================================
echo CAE-CLI 测试运行器
echo ========================================
echo.

:: 检查 Python 是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请确保已正确安装
    pause
    exit /b 1
)

:: 运行 Python 测试脚本
python run_tests.py %*

:: 检查测试是否成功
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] 测试完成！
) else (
    echo.
    echo [ERROR] 测试失败！
)

echo.
pause