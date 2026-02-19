# 安装和配置指南

## 快速安装

### 1. 安装 MCP 服务器

```bash
# 方式1：使用 pip（推荐）
pip install freecad-parametric-mcp

# 方式2：从源码安装
git clone https://github.com/yourusername/freecad-parametric-mcp.git
cd freecad-parametric-mcp
pip install -e .
```

### 2. 安装 FreeCAD 插件

#### 方式A：通过 FreeCAD Addon Manager（推荐）

1. 打开 FreeCAD
2. 转到 **Tools → Addon Manager**
3. 搜索 "ParametricMCP"
4. 点击安装并重启 FreeCAD

#### 方式B：手动安装

```bash
# Windows
cd %APPDATA%\FreeCAD\Mod
git clone https://github.com/yourusername/freecad-parametric-mcp.git ParametricMCP

# macOS
cd ~/Library/Application\ Support/FreeCAD/Mod
git clone https://github.com/yourusername/freecad-parametric-mcp.git ParametricMCP

# Linux
cd ~/.FreeCAD/Mod
git clone https://github.com/yourusername/freecad-parametric-mcp.git ParametricMCP
```

## 配置 Claude Desktop

编辑 `claude_desktop_config.json`：

### Windows
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

### macOS/Linux
```json
{
  "mcpServers": {
    "freecad-parametric": {
      "command": "python3",
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

### 配置文件位置

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## 启动步骤

### 1. 启动 FreeCAD 并运行 MCP 桥接

在 FreeCAD 中：
1. 切换到 **ParametricMCP** 工作区
2. 点击 **Start MCP Bridge** 按钮
3. 确认控制台显示 "MCP Bridge started on port 9875"

### 2. 启动 Claude Desktop

重启 Claude Desktop，它会自动连接到 FreeCAD。

## 验证安装

在 Claude 中测试：

```
请帮我创建一个参数组叫 "test_design"，然后添加一个参数 "width" 值为 100。
```

如果成功，你会看到 FreeCAD 中创建了参数表格。

## 高级配置

### 使用 UV 运行（推荐开发者）

```json
{
  "mcpServers": {
    "freecad-parametric": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/freecad-parametric-mcp",
        "python",
        "-m",
        "freecad_parametric_mcp.server"
      ]
    }
  }
}
```

### 使用 Mise 管理 Python 版本

```toml
# .mise.toml
[tools]
python = "3.11"

[env]
FREECAD_MODE = "xmlrpc"
```

### 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FREECAD_MODE` | 连接模式 (xmlrpc/socket/embedded) | `xmlrpc` |
| `FREECAD_HOST` | FreeCAD 主机地址 | `localhost` |
| `FREECAD_PORT` | FreeCAD 端口 | `9875` |
| `FREECAD_TIMEOUT` | 超时时间（毫秒） | `30000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 故障排除

### 问题：无法连接到 FreeCAD

**症状**: "Failed to connect to FreeCAD"

**解决**:
1. 确认 FreeCAD 已启动
2. 确认 MCP Bridge 已启动（查看 FreeCAD 控制台）
3. 检查端口 9875 是否被占用
4. 检查防火墙设置

### 问题：工具调用失败

**症状**: "Error: Sketch not found"

**解决**:
1. 确保在调用工具前 FreeCAD 文档已创建
2. 检查对象名称是否正确
3. 查看 FreeCAD 控制台了解详细错误

### 问题：参数更新不生效

**症状**: 修改参数后模型没有变化

**解决**:
1. 检查参数公式是否正确
2. 手动调用 `recompute_document`
3. 检查是否有循环依赖

## 性能优化

### 大模型优化

对于复杂模型（100+ 特征）：

1. 关闭自动重生成：
   ```json
   {
     "regenerate": false
   }
   ```

2. 批量更新参数后手动重生成：
   ```
   update_parameter 调用（regenerate=false）
   ...
   recompute_document
   ```

### 多文档工作

支持同时处理多个文档：

```python
# 切换活动文档
await mcp.activate_document({"name": "Design_A"})

# 在特定文档中操作
await mcp.add_parameter({
    "document": "Design_B",
    "group": "params",
    "name": "length",
    "value": 100
})
```

## 示例工作流

### 1. 快速开始 - 创建一个简单的参数化盒子

```
1. 创建参数组 "box_design"
2. 添加参数 length=100, width=50, height=30
3. 创建草图 "Box_Base" 在 XY 平面
4. 添加矩形 0,0 到 length,width
5. 拉伸草图，高度为 height
6. 完成！
```

### 2. 参数族生成

```
1. 创建设计表 "Box_Family"
2. 定义参数：length, width, height
3. 添加数据行（5种尺寸组合）
4. 批量生成参数族
5. 导出为不同格式（STEP, STL）
```

### 3. 设计优化

```
1. 创建基础模型
2. 运行参数敏感性分析
3. 识别关键参数
4. 调整参数范围
5. 生成优化报告
```

## 下一步

- 查看 [示例](examples/) 目录
- 阅读 [API 文档](docs/api.md)
- 学习 [高级技巧](docs/advanced.md)
