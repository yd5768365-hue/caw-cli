# API 参考

## 核心模块

| 模块 | 说明 |
|------|------|
| `sw_helper.geometry` | 几何解析 |
| `sw_helper.mesh` | 网格分析 |
| `sw_helper.material` | 材料数据库 |
| `sw_helper.mechanics` | 力学计算 |
| `sw_helper.ai` | AI 功能 |

## 使用示例

### 几何解析

```python
from sw_helper.geometry import GeometryParser

parser = GeometryParser()
data = parser.parse("model.step")
```

### 材料查询

```python
from sw_helper.material import MaterialDatabase

db = MaterialDatabase()
q235 = db.get_material("Q235")
```

### 力学计算

```python
from sw_helper.mechanics import MechanicsCalculator

calc = MechanicsCalculator()
result = calc.calculate_stress(force=10000, area=0.001)
```

### AI 学习助手

```python
from sw_helper.ai.prompt_manager import PromptManager

prompt = PromptManager.build_system_prompt("learning")
```
