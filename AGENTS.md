# AGENTS.md - CAE-CLI 开发指南

AI 代理开发指南,包含构建/测试命令和代码风格。

## 项目信息

- **Python**: >= 3.8 | **测试**: pytest | **格式**: Black (100字符) | **类型**: mypy

## 安装命令

```bash
pip install -e .           # 基础
pip install -e ".[full]"   # 完整功能(含几何处理)
pip install -e ".[dev]"    # 开发依赖
pip install -e ".[ssh]"    # SSH增强功能
pip install -e ".[tools]"  # 网格分析工具
```

## 运行 CLI

```bash
cae-cli --help             # 查看帮助
cae-cli version            # 版本号
cae-cli info               # 系统信息
cae-cli parse model.step   # 解析几何
cae-cli analyze mesh.msh   # 分析网格
cae-cli material Q235      # 查询材料
python -m sw_helper --help  # 模块方式运行
```

## 测试命令

```bash
pytest                          # 所有测试
pytest -v --tb=short           # 详细输出
pytest tests/test_cli.py       # 单文件
pytest tests/test_cli.py::test_func -v  # 单函数
pytest tests/test_cli.py::TestClass -v  # 单类
pytest --cov=src/sw_helper     # 覆盖率
pytest --lf                    # 上次失败
pytest -x                      # 快速失败
```

## 代码质量

```bash
black src/; black --check src/           # 格式化
mypy src/sw_helper; mypy --strict src/  # 类型检查
ruff check src/; ruff format --check src/  # Linting
```

## 代码风格

### 导入顺序
标准库 → 第三方 → 本地模块 (空行分隔,按字母排序)

### 命名
- 类: `PascalCase` - 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE` - 私有: `_prefix`

### 类型提示 (必须)
```python
def get_material(self, name: str) -> Optional[Dict[str, Any]]: ...
def calculate_stress(force: float, area: float) -> Dict[str, float]: ...
```

### 文档字符串 (Google风格)
```python
def func(arg: str) -> bool:
    """简短描述。

    Args:
        arg: 参数说明

    Returns:
        返回值说明

    Raises:
        ValueError: 条件说明
    """
```

### 错误处理
使用具体异常,提供有用信息:
```python
if not path.exists():
    raise FileNotFoundError(f"文件不存在: {path}")
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    raise ValueError(f"JSON无效: {e}")
```

### 文件操作
始终 UTF-8 编码,使用 pathlib:
```python
with open(path, "r", encoding="utf-8") as f: ...
path = Path.home() / ".cae-cli"
path.mkdir(exist_ok=True)
```

## 项目结构

```
src/sw_helper/
├── cli.py          # CLI入口
├── geometry/       # 几何解析
├── mesh/           # 网格分析
├── material/       # 材料力学
├── mechanics/      # 力学计算
├── report/         # 报告生成
├── optimization/   # 参数优化
├── ai/             # AI辅助
├── chat/           # 交互聊天
├── integrations/   # CAD集成
├── mcp/            # MCP协议
└── utils/          # 工具
```

## 提交前检查

```bash
pytest && black src/ && mypy src/sw_helper
```

## 故障排除

- 导入错误: 使用 `pip install -e .` 开发安装
- 测试失败: 检查 `test_data/` 目录是否存在
- 类型错误: 确保所有函数有类型提示
- Black 格式化: 运行 `black src/` 自动修复
- 创建虚拟环境: `python -m venv venv && venv\Scripts\activate`

## 关键配置 (pyproject.toml)

```toml
[tool.black]
line-length = 100
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

---
*更新: 2026-02-20*
