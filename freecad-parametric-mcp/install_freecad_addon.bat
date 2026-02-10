@echo off
chcp 65001
cls
echo ============================================
echo FreeCAD Parametric MCP 安装脚本
echo ============================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [管理员模式]
) else (
    echo [普通用户模式]
    echo 提示: 以管理员身份运行可以安装到系统范围
    echo.
)

:: Find FreeCAD Mod directory
set "FREECAD_MOD="

if exist "%APPDATA%\FreeCAD\Mod" (
    set "FREECAD_MOD=%APPDATA%\FreeCAD\Mod"
    echo ✓ 找到 FreeCAD 模块目录: %FREECAD_MOD%
) else (
    echo ✗ 未找到 FreeCAD 模块目录
    echo   请确保 FreeCAD 已安装
    pause
    exit /b 1
)

:: Check if already installed
if exist "%FREECAD_MOD%\ParametricMCP" (
    echo.
    echo [!] 检测到已存在的安装
    choice /C YN /M "是否覆盖安装"
    if errorlevel 2 goto :skip_install
    if errorlevel 1 (
        echo 删除旧版本...
        rmdir /S /Q "%FREECAD_MOD%\ParametricMCP"
    )
)

:: Copy files
echo.
echo 正在安装插件...
robocopy /E /NFL /NDL /NJH /NJS "%~dp0addon\ParametricMCP" "%FREECAD_MOD%\ParametricMCP"

if %errorlevel% LEQ 7 (
    echo ✓ 插件安装成功!
) else (
    echo ✗ 安装失败
    pause
    exit /b 1
)

:skip_install
echo.
echo ============================================
echo 安装完成!
echo ============================================
echo.
echo 下一步:
echo 1. 打开 FreeCAD
echo 2. 选择 "Parametric MCP" 工作区
echo 3. 点击 "Start MCP Bridge"
echo 4. 配置 Claude Desktop
echo.
echo 配置文件位置:
echo %APPDATA%\Claude\claude_desktop_config.json
echo.
pause
