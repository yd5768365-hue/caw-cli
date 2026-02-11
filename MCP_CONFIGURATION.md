# GitHub仓库管理MCP服务器配置指南

本指南介绍如何将GitHub仓库管理MCP服务器集成到Claude Code中，以便AI可以直接操作 `https://github.com/yd5768365-hue/caw-cli.git` 仓库。

## 📋 功能概述

GitHub仓库管理MCP服务器提供以下工具：

### 文件操作工具
- `github_repo_info` - 获取GitHub仓库基本信息
- `github_list_files` - 列出仓库中的文件
- `github_read_file` - 读取文件内容
- `github_write_file` - 写入文件内容（创建或覆盖）
- `github_create_file` - 创建新文件
- `github_delete_file` - 删除文件
- `github_rename_file` - 重命名或移动文件

### Git 操作工具
- `github_git_status` - 查看Git仓库状态
- `github_git_add` - 添加文件到Git暂存区
- `github_git_commit` - 提交更改到Git仓库
- `github_git_push` - 推送提交到远程仓库
- `github_git_pull` - 从远程仓库拉取更新
- `github_git_log` - 查看Git提交历史
- `github_git_create_branch` - 创建新分支
- `github_git_checkout` - 切换分支

## 🚀 配置步骤

### 步骤1: 验证MCP服务器

首先，测试MCP服务器是否可以正常运行：

```bash
# 测试简单导入
python test_mcp_simple.py

# 运行完整演示
python demo_github_mcp.py
```

### 步骤2: 创建MCP服务器启动脚本

我们已经创建了 `run_github_mcp.py`，这是一个基于stdio的MCP服务器，符合Claude Code的MCP协议要求。

### 步骤3: 配置Claude Code

#### Windows系统配置

1. **打开Claude Code配置目录**：
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

   或通过Claude Code设置界面配置MCP服务器。

2. **编辑配置文件**，添加以下内容：

```json
{
  "mcpServers": {
    "github-cae-cli": {
      "command": "python",
      "args": [
        "E:\\cae-cli\\run_github_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "E:\\cae-cli\\src"
      }
    }
  }
}
```

**注意**：请将 `E:\\cae-cli` 替换为你的实际项目路径。

#### macOS/Linux系统配置

1. **打开Claude Code配置目录**：
   ```
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **编辑配置文件**，添加以下内容：

```json
{
  "mcpServers": {
    "github-cae-cli": {
      "command": "python3",
      "args": [
        "/path/to/cae-cli/run_github_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/cae-cli/src"
      }
    }
  }
}
```

### 步骤4: 验证配置

1. **重启Claude Code** 以使配置生效
2. **运行 `/mcp` 命令** 检查MCP服务器是否已加载
3. **运行 `/doctor` 命令** 诊断MCP配置问题

## 🔧 故障排除

### 常见问题1: MCP服务器未加载
- **症状**: 运行 `/mcp` 显示 "No MCP servers configured"
- **解决**: 检查配置文件路径和格式是否正确，确保Claude Code有权限读取配置文件

### 常见问题2: Python路径错误
- **症状**: MCP服务器启动失败，提示模块导入错误
- **解决**: 确保 `PYTHONPATH` 环境变量正确设置，包含 `src` 目录

### 常见问题3: 权限问题
- **症状**: Claude Code无法执行Python脚本
- **解决**: 确保Python已正确安装，且脚本有可执行权限（Linux/macOS）

### 常见问题4: 路径包含空格
- **症状**: MCP服务器启动失败
- **解决**: 如果路径包含空格，使用引号包裹路径：
  ```json
  "args": [
    "\"C:\\My Projects\\cae-cli\\run_github_mcp.py\""
  ]
  ```

## 🧪 测试MCP服务器

### 手动测试

1. **启动MCP服务器测试**：
   ```bash
   python run_github_mcp.py
   ```

2. **发送测试消息**（在另一个终端）：
   ```bash
   echo '{"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}' | python run_github_mcp.py
   ```

3. **检查工具列表**：
   ```bash
   echo '{"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}}' | python run_github_mcp.py
   ```

### 通过Claude Code测试

配置完成后，在Claude Code中：
1. 输入 `/mcp` 查看已加载的MCP服务器
2. 尝试使用MCP工具，如：
   ```
   请使用github_repo_info工具获取仓库信息
   ```

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `src/sw_helper/mcp/github_server.py` | GitHub MCP服务器核心实现 |
| `run_github_mcp.py` | MCP服务器启动脚本（stdio模式） |
| `demo_github_mcp.py` | 功能演示脚本 |
| `test_mcp_simple.py` | 简单测试脚本 |
| `MCP_CONFIGURATION.md` | 配置指南（本文件） |

## 🛠️ 开发说明

### 添加新工具

要添加新的MCP工具，编辑 `src/sw_helper/mcp/github_server.py`：

1. 在 `_register_tools()` 方法中添加新的工具注册
2. 实现对应的 `_handle_*` 方法
3. 重启MCP服务器以使更改生效

### 调试MCP服务器

MCP服务器将所有日志输出到stderr，可以在Claude Code的MCP日志中查看：

1. 启用Claude Code的详细日志
2. 检查MCP服务器启动日志
3. 查看工具调用日志

## 🔄 更新与维护

### 更新MCP服务器
1. 修改源代码
2. 重启Claude Code以使更改生效

### 备份配置
建议备份Claude Code配置文件：
```bash
# Windows
copy %APPDATA%\Claude\claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json.backup

# macOS/Linux
cp ~/.config/Claude/claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json.backup
```

## 📞 支持与帮助

如果遇到问题：
1. 查看Claude Code官方文档：https://code.claude.com/docs/en/mcp
2. 检查项目GitHub Issues：https://github.com/yd5768365-hue/caw-cli/issues
3. 运行 `/doctor` 命令诊断问题

---

**配置成功提示**：配置完成后，AI将能够直接读取、修改、创建、删除仓库文件，并执行Git操作，实现自动化的仓库管理。