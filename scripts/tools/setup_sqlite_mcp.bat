@echo off
REM SQLite MCP 服务器设置脚本
REM 初始化数据库并配置 MCP 服务器

echo ========================================
echo    CAE-CLI SQLite MCP 服务器设置
echo ========================================

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 1. 检查 Node.js 和 npx
echo [1/3] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

npx --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 npx
    pause
    exit /b 1
)

echo [OK] Node.js 环境检查通过

REM 2. 初始化数据库
echo [2/3] 初始化 SQLite 数据库...
python init_sqlite_db.py
if errorlevel 1 (
    echo [ERROR] 数据库初始化失败
    pause
    exit /b 1
)

echo [OK] 数据库初始化完成

REM 3. 配置 MCP 服务器
echo [3/3] 配置 MCP 服务器...
echo 数据库路径: %CD%\data\cae.db

REM 删除已存在的同名服务器配置（可选）
claude mcp remove sqlite 2>nul
if errorlevel 1 (
    echo 未找到现有配置，继续...
)

REM 添加新的 MCP 服务器配置
echo 正在配置 MCP 服务器...
claude mcp add -s user sqlite -- npx -y @modelcontextprotocol/server-sqlite --db-path "%CD%\data\cae.db"

if errorlevel 1 (
    echo [ERROR] MCP 服务器配置失败
    pause
    exit /b 1
)

echo [OK] MCP 服务器配置成功

REM 4. 验证配置
echo.
echo 验证配置...
claude mcp list

echo.
echo ========================================
echo    设置完成！
echo ========================================
echo.
echo [DB] 数据库位置: %CD%\data\cae.db
echo [TOOL] MCP 服务器名称: sqlite
echo [CMD] 使用命令查看: claude mcp list
echo.
echo 现在可以在 Claude Code 中使用 SQLite MCP 工具了
echo.
pause