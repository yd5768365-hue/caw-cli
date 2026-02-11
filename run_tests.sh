#!/bin/bash
# CAE-CLI 测试运行器 - Linux/macOS 版本

set -e  # 遇到错误时立即停止

# 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # 无颜色

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}CAE-CLI 测试运行器${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} 未找到 Python，请确保已正确安装"
    exit 1
fi

# 检查项目是否已正确安装
if ! pip list | grep -q cae-cli; then
    echo -e "${YELLOW}[WARNING]${NC} 项目未安装，正在尝试开发模式安装..."
    pip install -e .[dev]
fi

# 运行 Python 测试脚本
python3 run_tests.py "$@"

# 检查测试是否成功
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} 测试完成！"
else
    echo -e "${RED}[ERROR]${NC} 测试失败！"
fi

echo ""