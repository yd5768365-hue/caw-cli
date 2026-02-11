"""
GitHub仓库管理 MCP Server - 将GitHub仓库操作暴露为MCP工具
专门针对 https://github.com/yd5768365-hue/caw-cli.git 仓库
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import json
import shutil
from datetime import datetime
from sw_helper.mcp.core import Tool, get_mcp_server


class GitHubRepoMCPServer:
    """
    GitHub仓库管理 MCP服务器
    为特定GitHub仓库提供文件操作和Git操作工具
    """

    def __init__(self, repo_path: Optional[str] = None):
        """
        初始化GitHub仓库MCP服务器

        Args:
            repo_path: 仓库本地路径，如果为None则使用当前工作目录
        """
        self.server = get_mcp_server()
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.repo_url = "https://github.com/yd5768365-hue/caw-cli.git"
        self._register_tools()

        print(f"[GitHub MCP] 初始化仓库管理服务器")
        print(f"[GitHub MCP] 仓库路径: {self.repo_path}")
        print(f"[GitHub MCP] 仓库URL: {self.repo_url}")

    def _register_tools(self):
        """注册所有GitHub仓库管理工具"""

        # 1. 仓库基本信息
        self.server.register_tool(
            Tool(
                name="github_repo_info",
                description="获取GitHub仓库基本信息",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_repo_info,
            )
        )

        # 2. 列出文件
        self.server.register_tool(
            Tool(
                name="github_list_files",
                description="列出仓库中的文件",
                input_schema={
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "目录路径（相对仓库根目录）",
                            "default": "."
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "是否递归列出",
                            "default": False
                        },
                        "pattern": {
                            "type": "string",
                            "description": "文件匹配模式（如*.py）",
                            "default": "*"
                        }
                    }
                },
                handler=self._handle_list_files,
            )
        )

        # 3. 读取文件内容
        self.server.register_tool(
            Tool(
                name="github_read_file",
                description="读取文件内容",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "文件路径（相对仓库根目录）"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码",
                            "default": "utf-8"
                        }
                    },
                    "required": ["file_path"]
                },
                handler=self._handle_read_file,
            )
        )

        # 4. 写入文件内容
        self.server.register_tool(
            Tool(
                name="github_write_file",
                description="写入文件内容（创建或覆盖）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "文件路径（相对仓库根目录）"
                        },
                        "content": {
                            "type": "string",
                            "description": "文件内容"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码",
                            "default": "utf-8"
                        },
                        "create_dirs": {
                            "type": "boolean",
                            "description": "是否自动创建目录",
                            "default": True
                        }
                    },
                    "required": ["file_path", "content"]
                },
                handler=self._handle_write_file,
            )
        )

        # 5. 创建新文件
        self.server.register_tool(
            Tool(
                name="github_create_file",
                description="创建新文件",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "文件路径（相对仓库根目录）"
                        },
                        "content": {
                            "type": "string",
                            "description": "文件内容",
                            "default": ""
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码",
                            "default": "utf-8"
                        }
                    },
                    "required": ["file_path"]
                },
                handler=self._handle_create_file,
            )
        )

        # 6. 删除文件
        self.server.register_tool(
            Tool(
                name="github_delete_file",
                description="删除文件",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "文件路径（相对仓库根目录）"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "是否强制删除",
                            "default": False
                        }
                    },
                    "required": ["file_path"]
                },
                handler=self._handle_delete_file,
            )
        )

        # 7. 重命名/移动文件
        self.server.register_tool(
            Tool(
                name="github_rename_file",
                description="重命名或移动文件",
                input_schema={
                    "type": "object",
                    "properties": {
                        "old_path": {
                            "type": "string",
                            "description": "原文件路径"
                        },
                        "new_path": {
                            "type": "string",
                            "description": "新文件路径"
                        },
                        "overwrite": {
                            "type": "boolean",
                            "description": "是否覆盖已存在的文件",
                            "default": False
                        }
                    },
                    "required": ["old_path", "new_path"]
                },
                handler=self._handle_rename_file,
            )
        )

        # 8. Git状态
        self.server.register_tool(
            Tool(
                name="github_git_status",
                description="查看Git仓库状态",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_git_status,
            )
        )

        # 9. Git添加文件
        self.server.register_tool(
            Tool(
                name="github_git_add",
                description="添加文件到Git暂存区",
                input_schema={
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "文件路径列表（相对仓库根目录）"
                        },
                        "all": {
                            "type": "boolean",
                            "description": "是否添加所有更改",
                            "default": False
                        }
                    }
                },
                handler=self._handle_git_add,
            )
        )

        # 10. Git提交
        self.server.register_tool(
            Tool(
                name="github_git_commit",
                description="提交更改到Git仓库",
                input_schema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "提交信息"
                        },
                        "author": {
                            "type": "string",
                            "description": "提交者信息",
                            "default": "Claude Code <noreply@anthropic.com>"
                        }
                    },
                    "required": ["message"]
                },
                handler=self._handle_git_commit,
            )
        )

        # 11. Git推送
        self.server.register_tool(
            Tool(
                name="github_git_push",
                description="推送提交到远程仓库",
                input_schema={
                    "type": "object",
                    "properties": {
                        "remote": {
                            "type": "string",
                            "description": "远程仓库名称",
                            "default": "origin"
                        },
                        "branch": {
                            "type": "string",
                            "description": "分支名称",
                            "default": "main"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "是否强制推送",
                            "default": False
                        }
                    }
                },
                handler=self._handle_git_push,
            )
        )

        # 12. Git拉取
        self.server.register_tool(
            Tool(
                name="github_git_pull",
                description="从远程仓库拉取更新",
                input_schema={
                    "type": "object",
                    "properties": {
                        "remote": {
                            "type": "string",
                            "description": "远程仓库名称",
                            "default": "origin"
                        },
                        "branch": {
                            "type": "string",
                            "description": "分支名称",
                            "default": "main"
                        }
                    }
                },
                handler=self._handle_git_pull,
            )
        )

        # 13. 查看提交历史
        self.server.register_tool(
            Tool(
                name="github_git_log",
                description="查看Git提交历史",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "显示最近的提交数量",
                            "default": 10
                        },
                        "format": {
                            "type": "string",
                            "description": "输出格式",
                            "enum": ["oneline", "short", "full", "graph"],
                            "default": "oneline"
                        }
                    }
                },
                handler=self._handle_git_log,
            )
        )

        # 14. 创建分支
        self.server.register_tool(
            Tool(
                name="github_git_create_branch",
                description="创建新分支",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "分支名称"
                        },
                        "start_point": {
                            "type": "string",
                            "description": "起始点（分支/提交）",
                            "default": "HEAD"
                        }
                    },
                    "required": ["branch_name"]
                },
                handler=self._handle_git_create_branch,
            )
        )

        # 15. 切换分支
        self.server.register_tool(
            Tool(
                name="github_git_checkout",
                description="切换分支",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "分支名称"
                        },
                        "create": {
                            "type": "boolean",
                            "description": "是否创建分支（如果不存在）",
                            "default": False
                        }
                    },
                    "required": ["branch_name"]
                },
                handler=self._handle_git_checkout,
            )
        )

        print(f"[GitHub MCP] 已注册 {len(self.server.tools)} 个仓库管理工具")

    # ===== 工具处理器 =====

    def _get_full_path(self, relative_path: str) -> Path:
        """获取文件的完整路径"""
        full_path = self.repo_path / relative_path
        # 安全验证：确保路径在仓库目录内
        try:
            full_path.resolve().relative_to(self.repo_path.resolve())
        except ValueError:
            raise ValueError(f"路径 {relative_path} 不在仓库目录内")
        return full_path

    def _run_git_command(self, args: List[str], capture_output: bool = True) -> Dict[str, Any]:
        """运行Git命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                encoding="utf-8"
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "command": f"git {' '.join(args)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": f"git {' '.join(args)}"
            }

    def _handle_repo_info(self) -> Dict[str, Any]:
        """处理仓库信息请求"""
        try:
            # 获取Git仓库信息
            remote_result = self._run_git_command(["remote", "-v"])
            branch_result = self._run_git_command(["branch", "--show-current"])
            status_result = self._run_git_command(["status", "--porcelain"])

            # 统计文件信息
            python_files = list(self.repo_path.rglob("*.py"))
            md_files = list(self.repo_path.rglob("*.md"))
            total_files = sum(1 for _ in self.repo_path.rglob("*") if _.is_file())

            return {
                "success": True,
                "repo_path": str(self.repo_path),
                "repo_url": self.repo_url,
                "current_branch": branch_result.get("stdout", "").strip(),
                "has_remote": "origin" in remote_result.get("stdout", ""),
                "uncommitted_changes": len(status_result.get("stdout", "").strip().splitlines()) if status_result.get("stdout") else 0,
                "file_stats": {
                    "total_files": total_files,
                    "python_files": len(python_files),
                    "markdown_files": len(md_files),
                    "directories": sum(1 for _ in self.repo_path.rglob("*/") if _.is_dir())
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_list_files(self, directory: str = ".", recursive: bool = False, pattern: str = "*") -> Dict[str, Any]:
        """处理列出文件请求"""
        try:
            target_dir = self._get_full_path(directory)
            if not target_dir.exists():
                return {"success": False, "error": f"目录不存在: {directory}"}

            if recursive:
                files = list(target_dir.rglob(pattern))
            else:
                files = list(target_dir.glob(pattern))

            # 过滤出文件（排除目录）
            file_list = []
            for file_path in files:
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.repo_path)
                    try:
                        stat = file_path.stat()
                        file_list.append({
                            "path": str(rel_path),
                            "name": file_path.name,
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "is_dir": False
                        })
                    except:
                        file_list.append({
                            "path": str(rel_path),
                            "name": file_path.name,
                            "is_dir": False
                        })

            # 如果非递归，也列出目录
            if not recursive:
                for dir_path in target_dir.iterdir():
                    if dir_path.is_dir():
                        rel_path = dir_path.relative_to(self.repo_path)
                        file_list.append({
                            "path": str(rel_path),
                            "name": dir_path.name,
                            "is_dir": True
                        })

            return {
                "success": True,
                "directory": directory,
                "recursive": recursive,
                "pattern": pattern,
                "count": len(file_list),
                "files": sorted(file_list, key=lambda x: x["path"])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """处理读取文件请求"""
        try:
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                return {"success": False, "error": f"文件不存在: {file_path}"}

            with open(full_path, "r", encoding=encoding) as f:
                content = f.read()

            stat = full_path.stat()
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "encoding": encoding
            }
        except UnicodeDecodeError:
            return {"success": False, "error": f"无法使用 {encoding} 编码读取文件"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_write_file(self, file_path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> Dict[str, Any]:
        """处理写入文件请求"""
        try:
            full_path = self._get_full_path(file_path)

            # 创建目录（如果需要）
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)

            # 备份原文件（如果存在）
            backup_path = None
            if full_path.exists():
                backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = full_path.with_suffix(f".{backup_time}.bak")
                shutil.copy2(full_path, backup_path)

            # 写入文件
            with open(full_path, "w", encoding=encoding) as f:
                f.write(content)

            # 获取文件信息
            stat = full_path.stat()
            return {
                "success": True,
                "file_path": file_path,
                "action": "modified" if backup_path else "created",
                "size": stat.st_size,
                "backup": str(backup_path) if backup_path else None,
                "encoding": encoding
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_create_file(self, file_path: str, content: str = "", encoding: str = "utf-8") -> Dict[str, Any]:
        """处理创建文件请求（确保文件不存在）"""
        try:
            full_path = self._get_full_path(file_path)
            if full_path.exists():
                return {"success": False, "error": f"文件已存在: {file_path}"}

            # 创建目录
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(full_path, "w", encoding=encoding) as f:
                f.write(content)

            stat = full_path.stat()
            return {
                "success": True,
                "file_path": file_path,
                "size": stat.st_size,
                "encoding": encoding
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_delete_file(self, file_path: str, force: bool = False) -> Dict[str, Any]:
        """处理删除文件请求"""
        try:
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                return {"success": False, "error": f"文件不存在: {file_path}"}

            if not force and full_path.is_file():
                # 如果不是强制删除，先备份
                backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = full_path.with_suffix(f".{backup_time}.bak")
                shutil.copy2(full_path, backup_path)

            # 删除文件或目录
            if full_path.is_file():
                full_path.unlink()
                action = "deleted"
            else:
                if force:
                    shutil.rmtree(full_path)
                    action = "force_deleted_directory"
                else:
                    return {"success": False, "error": "无法删除目录，请使用 force=True"}

            return {
                "success": True,
                "file_path": file_path,
                "action": action,
                "backup": str(backup_path) if not force and full_path.is_file() else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_rename_file(self, old_path: str, new_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """处理重命名文件请求"""
        try:
            old_full = self._get_full_path(old_path)
            new_full = self._get_full_path(new_path)

            if not old_full.exists():
                return {"success": False, "error": f"源文件不存在: {old_path}"}

            if new_full.exists() and not overwrite:
                return {"success": False, "error": f"目标文件已存在: {new_path}"}

            # 如果需要覆盖且目标文件存在，先备份
            backup_path = None
            if new_full.exists() and overwrite:
                backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = new_full.with_suffix(f".{backup_time}.bak")
                shutil.copy2(new_full, backup_path)

            # 移动文件
            old_full.rename(new_full)

            return {
                "success": True,
                "old_path": old_path,
                "new_path": new_path,
                "action": "renamed",
                "backup": str(backup_path) if backup_path else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_status(self) -> Dict[str, Any]:
        """处理Git状态请求"""
        try:
            # 获取详细状态
            result = self._run_git_command(["status", "--porcelain"])
            if not result["success"]:
                return result

            # 解析状态输出
            status_lines = result["stdout"].strip().splitlines()
            files = []
            for line in status_lines:
                if line:
                    status = line[:2].strip()
                    file_path = line[3:]
                    files.append({"status": status, "path": file_path})

            # 获取分支信息
            branch_result = self._run_git_command(["branch", "--show-current"])
            current_branch = branch_result.get("stdout", "").strip()

            # 获取远程信息
            remote_result = self._run_git_command(["remote", "-v"])

            return {
                "success": True,
                "current_branch": current_branch,
                "changed_files": len(files),
                "files": files,
                "has_remote": "origin" in remote_result.get("stdout", ""),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_add(self, files: Optional[List[str]] = None, all: bool = False) -> Dict[str, Any]:
        """处理Git添加请求"""
        try:
            if all:
                result = self._run_git_command(["add", "."])
            elif files:
                result = self._run_git_command(["add"] + files)
            else:
                return {"success": False, "error": "必须指定 files 参数或使用 all=True"}

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_commit(self, message: str, author: str = "Claude Code <noreply@anthropic.com>") -> Dict[str, Any]:
        """处理Git提交请求"""
        try:
            # 使用HEREDOC格式确保消息格式正确
            commit_command = ["commit", "-m", message]
            if author:
                commit_command.extend(["--author", author])

            result = self._run_git_command(commit_command)

            if result["success"]:
                # 获取提交哈希
                hash_result = self._run_git_command(["rev-parse", "HEAD"])
                if hash_result["success"]:
                    result["commit_hash"] = hash_result["stdout"].strip()

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_push(self, remote: str = "origin", branch: str = "main", force: bool = False) -> Dict[str, Any]:
        """处理Git推送请求"""
        try:
            command = ["push", remote, branch]
            if force:
                command.append("--force")

            result = self._run_git_command(command)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_pull(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        """处理Git拉取请求"""
        try:
            result = self._run_git_command(["pull", remote, branch])
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_log(self, limit: int = 10, format: str = "oneline") -> Dict[str, Any]:
        """处理Git日志请求"""
        try:
            format_map = {
                "oneline": "--oneline",
                "short": "--short",
                "full": "--full",
                "graph": "--graph --oneline"
            }

            format_arg = format_map.get(format, "--oneline")
            command = ["log", format_arg, f"-{limit}"]

            result = self._run_git_command(command)
            if result["success"]:
                # 解析提交日志
                commits = []
                lines = result["stdout"].strip().splitlines()
                for line in lines:
                    if line:
                        # 简单解析oneline格式
                        if " " in line:
                            hash_part, message = line.split(" ", 1)
                            commits.append({
                                "hash": hash_part,
                                "message": message.strip()
                            })
                        else:
                            commits.append({
                                "hash": line,
                                "message": ""
                            })

                result["commits"] = commits
                result["count"] = len(commits)

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_create_branch(self, branch_name: str, start_point: str = "HEAD") -> Dict[str, Any]:
        """处理创建分支请求"""
        try:
            result = self._run_git_command(["branch", branch_name, start_point])
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_checkout(self, branch_name: str, create: bool = False) -> Dict[str, Any]:
        """处理切换分支请求"""
        try:
            if create:
                result = self._run_git_command(["checkout", "-b", branch_name])
            else:
                result = self._run_git_command(["checkout", branch_name])
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局GitHub仓库 MCP Server实例
_github_mcp_server: Optional[GitHubRepoMCPServer] = None


def get_github_mcp_server(repo_path: Optional[str] = None) -> GitHubRepoMCPServer:
    """获取全局GitHub仓库MCP服务器"""
    global _github_mcp_server
    if _github_mcp_server is None:
        _github_mcp_server = GitHubRepoMCPServer(repo_path)
    return _github_mcp_server