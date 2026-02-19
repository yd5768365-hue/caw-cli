#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAE-CLI GUI 入口文件
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入并启动 GUI
from gui.web_gui import main

if __name__ == "__main__":
    main()
