# 开发指南

## 项目结构

```
cae-cli/
├── src/
│   ├── sw_helper/        # 主包
│   │   ├── cli.py       # CLI 入口
│   │   ├── geometry/    # 几何解析
│   │   ├── mesh/       # 网格分析
│   │   ├── material/   # 材料数据库
│   │   ├── mechanics/  # 力学计算
│   │   ├── ai/        # AI 模块
│   │   └── utils/     # 工具
│   ├── integrations/  # 插件化架构
│   └── gui/          # GUI
├── tests/             # 测试
└── knowledge/        # 知识库
```

## 开发环境

```bash
# 克隆项目
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli

# 安装开发依赖
pip install -e ".[dev]"
pip install -e ".[full]"
```

## 运行测试

```bash
# 所有测试
pytest

# 单个测试
pytest tests/unit/test_material.py -v

# 代码审查
cae-cli review --local

# 格式化
black src/
ruff check src/
```

## 代码规范

- Black 格式化 (100 字符)
- 类型注解 (Python 3.8+)
- Google 风格文档字符串

## 添加新功能

1. 在对应模块添加功能
2. 在 cli.py 添加命令
3. 添加单元测试
4. 更新文档
