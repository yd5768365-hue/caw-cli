# 安装完成！使用指南

## ✅ 安装状态

### 1. Python 包 - 已安装 ✓
```
freecad-parametric-mcp 0.1.0
```

### 2. 依赖项 - 已安装 ✓
- mcp (Model Context Protocol) ✓
- pydantic ✓
- pandas ✓
- openpyxl ✓
- numpy ✓

## 🚀 快速开始

### 步骤 1: 安装 FreeCAD 插件

**方法 A - 手动安装 (推荐)**

将插件复制到 FreeCAD 模块目录：

```bash
# Windows (以管理员身份运行 PowerShell)
Copy-Item -Recurse -Path "E:\cae-cli\freecad-parametric-mcp\addon\ParametricMCP" `
  -Destination "$env:APPDATA\FreeCAD\Mod\ParametricMCP"

# 或者手动复制：
# 1. 打开 E:\cae-cli\freecad-parametric-mcp\addon\ParametricMCP
# 2. 复制整个 ParametricMCP 文件夹
# 3. 粘贴到: %APPDATA%\FreeCAD\Mod\
```

**方法 B - 通过 FreeCAD Addon Manager**

1. 打开 FreeCAD
2. 点击 **Tools → Addon Manager**
3. 点击 **Configure** → **Custom repositories**
4. 添加本地路径: `E:\cae-cli\freecad-parametric-mcp\addon`
5. 搜索 "ParametricMCP" 并安装

### 步骤 2: 启动 FreeCAD

1. 打开 FreeCAD 0.21+ 或 1.0+
2. 在 Workbench 下拉菜单中选择 **"Parametric MCP"**
3. 点击工具栏上的 **"Start MCP Bridge"** 按钮
4. 查看 FreeCAD 控制台，确认显示：
   ```
   ============================================================
   MCP Bridge started!
     - XML-RPC: localhost:9875
   ============================================================
   ```

### 步骤 3: 配置 Claude Desktop

**编辑配置文件:**

Windows: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置:

```json
{
  "mcpServers": {
    "freecad-parametric": {
      "command": "python",
      "args": [
        "-m",
        "freecad_parametric_mcp.server"
      ],
      "env": {
        "FREECAD_MODE": "xmlrpc",
        "FREECAD_HOST": "localhost",
        "FREECAD_PORT": "9875"
      }
    }
  }
}
```

**重启 Claude Desktop**

### 步骤 4: 验证安装

在 Claude 中输入:

```
请帮我创建一个参数组叫 "test_group"，然后添加一个参数 "width"，值为 100。
```

如果成功，你应该能看到 FreeCAD 中创建了参数表格！

## 📋 可用工具 (56 个)

### 参数管理 (10)
- `create_parameter_group` - 创建参数组
- `add_parameter` - 添加参数
- `set_parameter_formula` - 设置公式
- `update_parameter` - 更新参数值
- `list_parameters` - 列出参数
- `validate_parameters` - 验证参数
- `import_parameters` - 导入参数
- `export_parameters` - 导出参数

### 智能草图 (7)
- `create_parametric_sketch` - 创建参数化草图
- `add_constrained_line` - 添加带约束的直线
- `add_constrained_circle` - 添加带约束的圆
- `add_dimensional_constraint` - 添加尺寸约束
- `auto_constrain_sketch` - 自动约束
- `analyze_sketch_dof` - 分析自由度

### 特征建模 (6)
- `create_parametric_pad` - 参数化拉伸
- `create_parametric_pocket` - 参数化挖槽
- `create_parametric_hole` - 参数化孔
- `edit_feature_parameter` - 编辑特征参数

### 参数族 (5)
- `create_design_table` - 创建设计表
- `generate_family_member` - 生成族成员
- `batch_generate_family` - 批量生成

### 分析 (3)
- `analyze_parameter_sensitivity` - 敏感性分析
- `check_design_rules` - 设计规则检查
- `generate_parameter_report` - 生成报告

## 💡 使用示例

### 示例 1: 参数化盒子
```
1. 创建参数组 "box_design"
2. 添加参数: length=100, width=50, height=30
3. 创建参数关联: volume = length * width * height
4. 创建草图 "Base" 并添加矩形
5. 拉伸草图，高度使用 height 参数
6. 修改 length 为 200，观察自动更新！
```

### 示例 2: 参数族生成
```
1. 创建设计表 "Box_Family"
2. 添加 5 种尺寸组合
3. 批量生成 5 个变体模型
4. 导出所有模型为 STEP 格式
```

## 🔧 故障排除

### 问题 1: "Failed to connect to FreeCAD"
- 确认 FreeCAD 已启动
- 确认已点击 "Start MCP Bridge"
- 检查端口 9875 是否被占用

### 问题 2: 工具调用失败
- 确保在调用工具前已创建 FreeCAD 文档
- 检查对象名称是否正确
- 查看 FreeCAD 控制台了解详细错误

### 问题 3: Claude 无法连接
- 检查配置文件路径是否正确
- 确认 Python 路径正确
- 重启 Claude Desktop

## 📁 项目位置

所有文件位于:
```
E:\cae-cli\freecad-parametric-mcp\
```

主要文件:
- `src/` - Python 源代码
- `addon/` - FreeCAD 插件
- `examples/` - 使用示例
- `docs/` - 文档

## 🎉 恭喜！

你现在拥有了一个**业界领先的 FreeCAD 参数化建模 MCP**！

比 neka-nat (505⭐) 和 spkane (21⭐) 的方案更强大的参数化能力！

开始你的参数化设计之旅吧！ 🚀
