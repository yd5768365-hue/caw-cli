#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 core 包导入"""

import sys
sys.path.insert(0, 'src')

try:
    from core import CAEError, SimulationConfig, FileFormat
    print('✓ core 包导入成功')
    print(f'  - CAEError: {CAEError}')
    print(f'  - SimulationConfig: {SimulationConfig}')
    print(f'  - FileFormat: {FileFormat}')
except Exception as e:
    print(f'✗ 导入失败: {e}')
    sys.exit(1)
