# CAE-CLI 开发者贡献指南 🤝

欢迎您参与 CAE-CLI 项目的开发！本指南将帮助您了解如何贡献代码、报告问题、改进文档和扩展功能。

## 🎯 贡献类型

### 1. 报告问题（Bug 报告）
### 2. 功能建议（新功能请求）
### 3. 贡献代码（功能开发、Bug 修复）
### 4. 改进文档（教程、API 文档、翻译）
### 5. 添加材料（扩展材料数据库）
### 6. 添加知识（扩展机械知识库）

---

## 1. 如何参与？

### 1.1 报告问题

如果您发现了 bug 或有功能建议，请：

1. **首先查看** [FAQ.md](FAQ.md) 确认是否已有解决方案
2. **搜索 Issues**：[GitHub Issues](https://github.com/yd5768365-hue/caw-cli/issues) 确认是否已有人报告
3. **创建新 Issue**（如未找到相关内容），包含：
   - **问题描述**：清晰、详细的问题说明
   - **复现步骤**：如何重现问题（1、2、3...）
   - **预期行为**：期望的结果是什么
   - **实际行为**：实际得到的结果是什么
   - **系统信息**：Windows 版本、Python 版本、CAE-CLI 版本、FreeCAD/CalculiX 版本
   - **错误信息**：完整的错误堆栈信息
   - **截图/日志**：相关截图或日志文件

### 1.2 提交代码

1. **Fork 仓库**：点击 GitHub 页面的 "Fork" 按钮
2. **克隆您的分支**：`git clone https://github.com/您的用户名/caw-cli.git`
3. **创建功能分支**：`git checkout -b feature/功能名称`
4. **开发并测试**：编写代码，运行测试
5. **提交更改**：`git commit -am '添加新功能：xxx'`
6. **推送到分支**：`git push origin feature/功能名称`
7. **创建 Pull Request**：在 GitHub 上创建 PR，使用提供的模板

## 2. 开发环境搭建 🔧

### 2.1 克隆仓库

```bash
git clone https://github.com/yourusername/cae-cli.git
cd cae-cli
```

### 2.2 安装依赖

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 或安装完整功能版
pip install -e ".[full]"
```

### 2.3 验证安装

```bash
# 运行测试
pytest

# 检查代码格式
black --check src/

# 运行类型检查
mypy src/sw_helper src/integrations src/core
```

## 3. 编码规范 📋

### 3.1 代码风格

- 使用 **Black** 进行代码格式化
- 使用 **mypy** 进行类型检查
- 遵循 **PEP 8** 规范
- 使用 **Google 风格** 的文档字符串

### 3.2 文档字符串示例

```python
"""
函数/类的功能描述（一句话）

详细描述函数的功能、参数、返回值和异常。

Args:
    param1: 参数1的描述
    param2: 参数2的描述

Returns:
    返回值的描述

Raises:
    ExceptionType: 异常情况的描述
"""
```

### 3.3 提交消息规范

```
类型: 主题（不超过50字符）

详细描述（可选，换行后，每行不超过72字符）
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档修改
- `style`: 代码风格调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他变更

**示例：**
```
feat: 添加材料属性查询功能

- 新增 material 命令
- 支持查询弹性模量、泊松比等参数
- 新增 materials.json 材料库
```

## 4. 扩展项目内容 📚

### 4.1 如何添加材料

CAE-CLI 的材料数据库位于 `data/materials.json`，您可以添加新材料来扩展数据库。

#### 材料数据结构
```json
{
  "材料名称": {
    "name": "材料显示名称",
    "category": "材料类别",  // 如 "steel", "aluminum", "titanium"
    "standard": "标准编号",  // 如 "GB/T 700-2006"
    "elastic_modulus": 210000000000,  // 弹性模量 (Pa)
    "poisson_ratio": 0.3,             // 泊松比
    "yield_strength": 235000000,      // 屈服强度 (Pa)
    "tensile_strength": 375000000,    // 抗拉强度 (Pa)
    "density": 7850,                  // 密度 (kg/m³)
    "thermal_expansion": 0.000012,    // 热膨胀系数 (1/K)
    "thermal_conductivity": 50.0,     // 导热系数 (W/m·K)
    "specific_heat": 450.0,           // 比热容 (J/kg·K)
    "description": "材料描述"
  }
}
```

#### 添加步骤
1. **备份原文件**：`cp data/materials.json data/materials.json.backup`
2. **编辑材料文件**：在 `data/materials.json` 中添加新材料条目
3. **验证格式**：运行 `python -m json.tool data/materials.json` 检查 JSON 格式
4. **测试查询**：`cae-cli material 新材料名称`
5. **提交更改**：提交包含新材料的数据文件

#### 示例：添加 304 不锈钢
```json
"304StainlessSteel": {
  "name": "304 不锈钢",
  "category": "stainless_steel",
  "standard": "ASTM A240",
  "elastic_modulus": 193000000000,
  "poisson_ratio": 0.29,
  "yield_strength": 205000000,
  "tensile_strength": 515000000,
  "density": 8000,
  "thermal_expansion": 0.0000172,
  "thermal_conductivity": 16.2,
  "specific_heat": 500,
  "description": "奥氏体不锈钢，具有良好的耐腐蚀性和成形性"
}
```

### 4.2 如何添加知识

机械知识库位于 `data/knowledge/` 目录（规划中），支持 Markdown 格式的知识条目。

#### 知识库结构
```
data/knowledge/
├── materials/          # 材料知识
│   ├── steels.md      # 钢材知识
│   ├── aluminum.md    # 铝合金知识
│   └── composites.md  # 复合材料知识
├── standards/         # 标准规范
│   ├── gb_standards.md  # 国标
│   └── iso_standards.md # ISO标准
├── formulas/          # 公式手册
│   ├── stress_strain.md  # 应力应变公式
│   └── buckling.md      # 屈曲公式
└── design_rules/      # 设计规范
    ├── weld_design.md   # 焊接设计
    └── fatigue_design.md # 疲劳设计
```

#### 添加知识步骤
1. **创建知识文件**：在相应目录下创建 `.md` 文件
2. **编写内容**：使用 Markdown 格式，包含清晰的标题和结构
3. **添加元数据**：在文件开头添加 YAML 元数据
   ```markdown
   ---
   title: "钢材知识"
   category: "materials"
   tags: ["steel", "material", "properties"]
   created: "2026-02-12"
   updated: "2026-02-12"
   author: "您的名字"
   ---
   ```
4. **测试查询**：通过 `cae-cli knowledge` 命令测试检索功能
5. **提交更改**：提交新知识文件

### 4.3 如何贡献代码

#### 代码贡献流程
1. **选择任务**：从 [GitHub Issues](https://github.com/yd5768365-hue/caw-cli/issues) 选择要解决的问题
2. **理解架构**：阅读本指南的架构设计部分，了解代码结构
3. **编写代码**：遵循编码规范，添加适当注释
4. **添加测试**：为新功能编写单元测试和集成测试
5. **运行测试**：确保所有测试通过
6. **更新文档**：更新相关文档（API 文档、用户指南等）
7. **提交 PR**：创建 Pull Request，使用 PR 模板

#### 代码审查标准
- ✅ **功能正确**：实现需求，无 bug
- ✅ **代码规范**：符合 Black 和 mypy 要求
- ✅ **测试覆盖**：有适当的测试用例
- ✅ **文档更新**：更新了相关文档
- ✅ **向后兼容**：不影响现有功能
- ✅ **性能合理**：无明显性能问题

## 5. 架构设计 📐

### 4.1 项目结构

```
cae-cli/
├── src/
│   ├── sw_helper/           # 主包（原有功能）
│   ├── integrations/       # 插件化架构（全新）
│   │   ├── _base/          # 抽象基类
│   │   ├── cad/            # CAD连接器实现
│   │   ├── cae/            # CAE连接器实现
│   │   └── mesher/         # 网格生成器
│   └── core/               # 核心数据类型
├── data/                    # 数据文件
├── tests/                   # 测试
├── examples/                # 示例
├── docs/                    # 文档
└── pyproject.toml          # 项目配置
```

### 4.2 核心架构

#### 插件化架构
- `CADConnector`：CAD软件连接器抽象基类
- `CAEConnector`：CAE软件连接器抽象基类
- `WorkflowEngine`：工作流引擎

#### 已实现的连接器
- **CAD: FreeCAD**：标准化连接器，支持参数修改、重建、导出
- **CAE: CalculiX**：开源有限元分析软件集成

## 5. 功能开发流程 🎯

### 5.1 新增 CLI 命令

1. 在 `src/sw_helper/cli.py` 中添加新命令
2. 实现命令功能（可参考已有命令）
3. 添加测试用例到 `tests/` 目录
4. 更新文档（QUICKSTART.md、API_REFERENCE.md 等）

### 5.2 新增插件

1. 在 `src/integrations/` 目录下创建新的连接器
2. 继承对应的抽象基类（CADConnector 或 CAEConnector）
3. 实现所有抽象方法
4. 在 `src/integrations/__init__.py` 中导出新连接器
5. 添加测试用例

## 6. 测试指南 🧪

### 6.1 运行测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_cli.py -v

# 运行测试并生成 HTML 报告
python run_tests.py

# 清理旧报告并运行测试
python run_tests.py --clean
```

### 6.2 测试结构

测试文件应放在 `tests/` 目录下，命名格式为 `test_*.py`。

**示例：**
```python
import pytest
from sw_helper.cli import main

def test_cli_help():
    """测试 --help 命令"""
    result = main(["--help"])
    assert result == 0
```

## 7. 文档编写 📝

### 7.1 更新文档

- **README.md**：项目概览、快速开始
- **QUICKSTART.md**：5分钟上手指南
- **INSTALLATION_GUIDE.md**：详细安装说明
- **FAQ.md**：常见问题解答
- **CONTRIBUTING.md**：本指南
- **API_REFERENCE.md**：API 参考（自动生成）

### 7.2 生成 API 文档

```bash
# 生成 API 文档
python -m pdoc --html --output-dir docs/api src/sw_helper src/integrations src/core
```

## 8. 版本控制 📦

### 8.1 版本号规范

使用语义化版本控制（Semantic Versioning）：
- **主版本号**：不兼容的 API 变更
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 8.2 发布流程

1. 更新版本号（在 `pyproject.toml` 和 `src/sw_helper/__init__.py` 中）
2. 运行所有测试，确保通过
3. 提交更改
4. 创建发布标签：`git tag vX.Y.Z`
5. 推送标签：`git push origin vX.Y.Z`
6. 在 GitHub 上创建发布

## 9. Pull Request 模板 📝

创建 Pull Request 时，请使用以下模板格式。这将帮助审查者快速理解您的更改。

### PR 模板内容
```markdown
## 描述
<!-- 简要描述这个 PR 做了什么 -->

## 变更类型
<!-- 请选择适当的类型（可多选） -->
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 测试添加/更新
- [ ] 配置变更
- [ ] 其他（请说明）

## 相关 Issue
<!-- 关联的 GitHub Issue，格式：fix #123 或 close #456 -->
fix #

## 变更内容
<!-- 详细描述具体变更内容 -->

### 修改的文件
- `path/to/file1.py` - 描述修改内容
- `path/to/file2.md` - 描述修改内容

### 新增的功能
1. 功能1描述
2. 功能2描述

### 修复的问题
1. 问题1描述
2. 问题2描述

## 测试
<!-- 描述如何测试这些变更 -->

### 测试步骤
1. 步骤1
2. 步骤2

### 测试结果
- [ ] 所有测试通过
- [ ] 新增测试通过
- [ ] 手动测试通过

## 检查清单
- [ ] 代码符合 Black 代码风格
- [ ] 通过 mypy 类型检查
- [ ] 添加/更新了相关测试
- [ ] 更新了相关文档
- [ ] 提交消息遵循规范
- [ ] 不影响现有功能

## 截图/示例
<!-- 如果适用，添加截图或示例 -->

## 其他说明
<!-- 任何其他需要说明的内容 -->
```

### PR 审查流程
1. **自动检查**：GitHub Actions 运行测试和代码检查
2. **代码审查**：至少需要一名核心贡献者批准
3. **合并条件**：
   - ✅ 所有自动化检查通过
   - ✅ 至少一名审查者批准
   - ✅ 解决所有审查评论
   - ✅ 无冲突
4. **合并方式**：Squash and merge（推荐）或 Rebase and merge

### 常见问题
- **PR 被拒绝**：根据反馈修改后重新提交
- **合并冲突**：从主分支拉取最新更改并解决冲突
- **长时间未审查**：@ 提及相关维护者请求审查

## 11. 社区规范 🤗

### 11.1 行为准则

我们遵循 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则，确保社区友好和包容性。

### 11.2 沟通方式

- **GitHub Issues**：问题跟踪和功能请求
- **QQ 群**：技术交流（[CAE-CLI 技术交流群]）
- **邮件**：your@email.com

## 12. 知识产权 📄

### 12.1 许可证

CAE-CLI 采用 [MIT 许可证](https://opensource.org/licenses/MIT)。

### 12.2 贡献者许可协议

参与项目即表示您同意您的贡献将受 MIT 许可证约束。

## 13. 常见问题 🐛

### 13.1 如何解决编码问题？

```bash
# 临时解决方案
set PYTHONIOENCODING=utf-8

# 永久解决方案（添加到系统变量）
PYTHONIOENCODING=utf-8
```

### 13.2 如何调试 CLI 命令？

```bash
# 使用 verbose 模式
cae-cli --verbose parse model.step

# 或使用 Python 调试器
python -m debugpy --listen 5678 --wait-for-client -m sw_helper parse model.step
```

---

感谢您的贡献！让我们一起将 CAE-CLI 打造成机械专业学生的得力助手！ 🎉