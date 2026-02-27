"""
SSH增强的GitHub仓库管理 MCP Server
提供SSH密钥管理、SSH远程配置和更稳定的SSH-based Git操作
"""

import socket
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sw_helper.mcp.core import Tool, get_mcp_server

# 可选依赖：paramiko用于高级SSH测试
try:
    import paramiko

    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    print("[SSH MCP] 注意: paramiko未安装，高级SSH测试功能将受限")
    print("[SSH MCP] 安装: pip install paramiko")


class SSHEnhancedMCPServer:
    """
    SSH增强的GitHub仓库管理 MCP服务器
    提供SSH密钥管理和SSH-based Git操作
    """

    def __init__(self, repo_path: Optional[str] = None):
        """
        初始化SSH增强的MCP服务器

        Args:
            repo_path: 仓库本地路径，如果为None则使用当前工作目录
        """
        self.server = get_mcp_server()
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.repo_url = "https://github.com/yd5768365-hue/caw-cli.git"
        self.ssh_repo_url = "git@github.com:yd5768365-hue/caw-cli.git"
        self.ssh_config_dir = Path.home() / ".ssh"
        self._register_tools()

        print("[SSH MCP] 初始化SSH增强仓库管理服务器")
        print(f"[SSH MCP] 仓库路径: {self.repo_path}")
        print(f"[SSH MCP] HTTPS URL: {self.repo_url}")
        print(f"[SSH MCP] SSH URL: {self.ssh_repo_url}")

    def _register_tools(self):
        """注册所有SSH增强的工具"""

        # 1. SSH配置检查
        self.server.register_tool(
            Tool(
                name="ssh_check_config",
                description="检查SSH配置状态",
                input_schema={"type": "object", "properties": {}},
                handler=self._handle_ssh_check_config,
            )
        )

        # 2. 生成SSH密钥
        self.server.register_tool(
            Tool(
                name="ssh_generate_key",
                description="生成新的SSH密钥对",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key_type": {
                            "type": "string",
                            "description": "密钥类型 (rsa, ed25519)",
                            "default": "ed25519",
                            "enum": ["rsa", "ed25519"],
                        },
                        "key_size": {"type": "integer", "description": "密钥大小（仅适用于RSA）", "default": 4096},
                        "email": {
                            "type": "string",
                            "description": "邮箱地址（用于密钥注释）",
                            "default": "user@example.com",
                        },
                    },
                },
                handler=self._handle_ssh_generate_key,
            )
        )

        # 3. 测试SSH连接
        self.server.register_tool(
            Tool(
                name="ssh_test_connection",
                description="测试到GitHub的SSH连接",
                input_schema={
                    "type": "object",
                    "properties": {"host": {"type": "string", "description": "主机名", "default": "github.com"}},
                },
                handler=self._handle_ssh_test_connection,
            )
        )

        # 4. 配置SSH远程
        self.server.register_tool(
            Tool(
                name="ssh_configure_remote",
                description="配置Git仓库使用SSH远程",
                input_schema={
                    "type": "object",
                    "properties": {"remote_name": {"type": "string", "description": "远程名称", "default": "origin"}},
                },
                handler=self._handle_ssh_configure_remote,
            )
        )

        # 5. 网络诊断
        self.server.register_tool(
            Tool(
                name="network_diagnostic",
                description="网络连接诊断",
                input_schema={
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "测试目标列表",
                            "default": ["github.com", "google.com", "8.8.8.8"],
                        }
                    },
                },
                handler=self._handle_network_diagnostic,
            )
        )

        # 6. 使用SSH的Git推送（更稳定的版本）
        self.server.register_tool(
            Tool(
                name="ssh_git_push",
                description="使用SSH推送Git提交（更稳定）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "remote": {"type": "string", "description": "远程仓库名称", "default": "origin"},
                        "branch": {"type": "string", "description": "分支名称", "default": "main"},
                        "force": {"type": "boolean", "description": "是否强制推送", "default": False},
                        "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 30},
                    },
                },
                handler=self._handle_ssh_git_push,
            )
        )

        # 7. 获取SSH公钥
        self.server.register_tool(
            Tool(
                name="ssh_get_public_key",
                description="获取SSH公钥内容",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key_file": {
                            "type": "string",
                            "description": "密钥文件名（不含扩展名）",
                            "default": "id_ed25519",
                        }
                    },
                },
                handler=self._handle_ssh_get_public_key,
            )
        )

        # 8. 修复SSH主机密钥验证
        self.server.register_tool(
            Tool(
                name="ssh_fix_host_key",
                description="修复SSH主机密钥验证问题",
                input_schema={
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "主机名", "default": "github.com"},
                        "key_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "密钥类型",
                            "default": ["rsa", "ecdsa", "ed25519"],
                        },
                    },
                },
                handler=self._handle_ssh_fix_host_key,
            )
        )

        # 9. 检查Git远程配置
        self.server.register_tool(
            Tool(
                name="git_check_remote",
                description="检查Git远程配置",
                input_schema={
                    "type": "object",
                    "properties": {"remote_name": {"type": "string", "description": "远程名称", "default": "origin"}},
                },
                handler=self._handle_git_check_remote,
            )
        )

        print(f"[SSH MCP] 已注册 {len(self.server.tools)} 个SSH增强工具")

    # ===== 工具处理器 =====

    def _run_command(
        self, args: List[str], capture_output: bool = True, timeout: int = 30, cwd: Optional[Path] = None
    ) -> Dict[str, Any]:
        """运行命令"""
        try:
            result = subprocess.run(
                args,
                cwd=cwd or self.repo_path,
                capture_output=capture_output,
                text=True,
                encoding="utf-8",
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "command": " ".join(args),
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"命令超时 ({timeout}秒)", "command": " ".join(args)}
        except Exception as e:
            return {"success": False, "error": str(e), "command": " ".join(args)}

    def _run_git_command(self, args: List[str], capture_output: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """运行Git命令"""
        return self._run_command(["git"] + args, capture_output, timeout)

    def _handle_ssh_check_config(self) -> Dict[str, Any]:
        """检查SSH配置状态"""
        try:
            ssh_dir_exists = self.ssh_config_dir.exists()
            ssh_config_file = self.ssh_config_dir / "config"
            ssh_config_exists = ssh_config_file.exists()

            # 检查常见密钥文件
            key_files = []
            for key_type in ["id_rsa", "id_ed25519", "id_ecdsa"]:
                private_key = self.ssh_config_dir / key_type
                public_key = self.ssh_config_dir / f"{key_type}.pub"
                if private_key.exists():
                    key_files.append(
                        {
                            "name": key_type,
                            "private_exists": True,
                            "public_exists": public_key.exists(),
                            "private_size": private_key.stat().st_size if private_key.exists() else 0,
                        }
                    )

            # 检查known_hosts
            known_hosts = self.ssh_config_dir / "known_hosts"
            known_hosts_exists = known_hosts.exists()

            # 测试SSH代理
            ssh_agent_result = self._run_command(["ssh-add", "-l"], capture_output=True, timeout=5)
            ssh_agent_has_keys = ssh_agent_result["success"] and "no identities" not in ssh_agent_result.get(
                "stderr", ""
            )

            return {
                "success": True,
                "ssh_directory": str(self.ssh_config_dir),
                "ssh_dir_exists": ssh_dir_exists,
                "ssh_config_exists": ssh_config_exists,
                "known_hosts_exists": known_hosts_exists,
                "key_files": key_files,
                "ssh_agent_has_keys": ssh_agent_has_keys,
                "agent_result": ssh_agent_result if not ssh_agent_has_keys else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_ssh_generate_key(
        self, key_type: str = "ed25519", key_size: int = 4096, email: str = "user@example.com"
    ) -> Dict[str, Any]:
        """生成SSH密钥对"""
        try:
            # 确保SSH目录存在
            self.ssh_config_dir.mkdir(exist_ok=True, mode=0o700)

            # 生成密钥文件名
            key_name = f"id_{key_type}"
            private_key_path = self.ssh_config_dir / key_name
            public_key_path = self.ssh_config_dir / f"{key_name}.pub"

            # 检查密钥是否已存在
            if private_key_path.exists():
                return {
                    "success": False,
                    "error": f"密钥文件已存在: {private_key_path}",
                    "existing_key": str(private_key_path),
                }

            # 构建ssh-keygen命令
            comment = f"{email}"
            if key_type == "rsa":
                cmd = [
                    "ssh-keygen",
                    "-t",
                    "rsa",
                    "-b",
                    str(key_size),
                    "-C",
                    comment,
                    "-f",
                    str(private_key_path),
                    "-N",
                    "",
                ]
            else:  # ed25519
                cmd = ["ssh-keygen", "-t", "ed25519", "-C", comment, "-f", str(private_key_path), "-N", ""]

            result = self._run_command(cmd, capture_output=True, timeout=30)

            if result["success"]:
                # 读取公钥内容
                public_key_content = ""
                if public_key_path.exists():
                    with open(public_key_path, encoding="utf-8") as f:
                        public_key_content = f.read().strip()

                return {
                    "success": True,
                    "private_key": str(private_key_path),
                    "public_key": str(public_key_path),
                    "public_key_content": public_key_content,
                    "key_type": key_type,
                    "key_size": key_size if key_type == "rsa" else 256,  # ed25519固定256位
                    "comment": comment,
                    "instructions": "请将上面的公钥内容添加到GitHub: Settings → SSH and GPG keys → New SSH key",
                }
            else:
                return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_ssh_test_connection(self, host: str = "github.com") -> Dict[str, Any]:
        """测试SSH连接"""
        try:
            # 方法1: 使用ssh命令测试
            ssh_result = self._run_command(["ssh", "-T", f"git@{host}"], capture_output=True, timeout=10)

            # 方法2: 使用socket测试SSH端口
            port_test_result = self._test_port(host, 22)

            # 方法3: 使用paramiko进行更详细的测试（如果可用）
            paramiko_result = None
            if PARAMIKO_AVAILABLE:
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(host, port=22, username="git", timeout=5)
                    paramiko_result = {"success": True, "connection": "SSH连接成功"}
                    client.close()
                except Exception as e:
                    paramiko_result = {"success": False, "error": str(e)}
            else:
                paramiko_result = {"success": False, "error": "paramiko未安装", "unavailable": True}

            return {
                "success": ssh_result["success"]
                or (
                    paramiko_result["success"] if paramiko_result and not paramiko_result.get("unavailable") else False
                ),
                "host": host,
                "ssh_command_result": ssh_result,
                "port_test": port_test_result,
                "paramiko_test": paramiko_result,
                "interpretation": self._interpret_ssh_test(ssh_result, paramiko_result),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_port(self, host: str, port: int) -> Dict[str, Any]:
        """测试端口连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return {"success": result == 0, "host": host, "port": port, "connection_result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _interpret_ssh_test(self, ssh_result: Dict[str, Any], paramiko_result: Dict[str, Any]) -> str:
        """解释SSH测试结果"""
        if ssh_result.get("success"):
            stdout = ssh_result.get("stdout", "").lower()
            stderr = ssh_result.get("stderr", "").lower()

            if "successfully authenticated" in stderr or "permission denied" in stderr:
                return "SSH连接成功，但认证失败（这是预期的，因为我们在测试连接而非认证）"
            elif "warning" in stderr or "hello" in stdout:
                return "SSH连接成功，可以连接到GitHub"
            else:
                return "SSH连接成功"
        elif paramiko_result and paramiko_result.get("success"):
            return "通过paramiko测试连接成功"
        elif paramiko_result and paramiko_result.get("unavailable"):
            return "SSH命令测试失败，paramiko未安装（安装: pip install paramiko）"
        else:
            return "SSH连接失败，请检查网络和SSH配置"

    def _handle_ssh_configure_remote(self, remote_name: str = "origin") -> Dict[str, Any]:
        """配置Git仓库使用SSH远程"""
        try:
            # 获取当前远程URL
            current_url_result = self._run_git_command(["remote", "get-url", remote_name])
            current_url = ""
            if current_url_result["success"]:
                current_url = current_url_result["stdout"].strip()

            # 设置SSH远程URL
            set_result = self._run_git_command(["remote", "set-url", remote_name, self.ssh_repo_url])

            # 验证设置
            verify_result = self._run_git_command(["remote", "get-url", remote_name])
            new_url = verify_result["stdout"].strip() if verify_result["success"] else ""

            return {
                "success": set_result["success"],
                "remote_name": remote_name,
                "old_url": current_url,
                "new_url": new_url,
                "ssh_url": self.ssh_repo_url,
                "action": "updated" if current_url else "set",
                "verification": verify_result,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_network_diagnostic(self, targets: List[str] = None) -> Dict[str, Any]:
        """网络连接诊断"""
        if targets is None:
            targets = ["github.com", "google.com", "8.8.8.8"]

        results = []
        for target in targets:
            # 测试ping
            ping_result = self._run_command(["ping", "-n", "2", target], capture_output=True, timeout=10)

            # 测试HTTP连接（针对github.com）
            http_result = None
            if "github.com" in target:
                try:
                    import requests

                    http_result = {"success": False, "error": "requests可用但未测试"}
                except ImportError:
                    http_result = {"success": False, "error": "requests库未安装"}

            # 测试端口
            port_results = {}
            for port in [22, 80, 443]:
                port_results[str(port)] = self._test_port(target, port)

            results.append({"target": target, "ping": ping_result, "http": http_result, "ports": port_results})

        # 总体评估
        overall_success = any(r["ping"]["success"] for r in results)

        return {
            "success": overall_success,
            "targets": results,
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_network_recommendations(results),
        }

    def _generate_network_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """生成网络诊断建议"""
        recommendations = []

        # 检查GitHub连接
        github_results = [r for r in results if "github.com" in r["target"]]
        if github_results:
            github = github_results[0]
            if not github["ping"]["success"]:
                recommendations.append("无法ping通github.com，请检查网络连接")
            if not github["ports"].get("22", {}).get("success"):
                recommendations.append("GitHub SSH端口(22)不可达，可能被防火墙阻挡")
            if not github["ports"].get("443", {}).get("success"):
                recommendations.append("GitHub HTTPS端口(443)不可达，可能被防火墙阻挡")

        # 通用建议
        if not any(r["ping"]["success"] for r in results):
            recommendations.append("所有目标都无法连接，请检查网络设置和防火墙")
        elif len([r for r in results if r["ping"]["success"]]) < len(results) / 2:
            recommendations.append("部分目标无法连接，网络可能不稳定")

        if not recommendations:
            recommendations.append("网络连接正常")

        return recommendations

    def _handle_ssh_git_push(
        self, remote: str = "origin", branch: str = "main", force: bool = False, timeout: int = 30
    ) -> Dict[str, Any]:
        """使用SSH推送Git提交（更稳定）"""
        try:
            # 构建推送命令
            command = ["push", remote, branch]
            if force:
                command.append("--force")

            # 添加详细输出以便调试
            command.append("-v")

            result = self._run_git_command(command, timeout=timeout)

            # 添加额外的诊断信息
            if not result["success"]:
                # 检查远程配置
                remote_result = self._run_git_command(["remote", "-v"])
                # 检查网络
                network_result = self._handle_network_diagnostic(["github.com"])

                result["diagnostics"] = {
                    "remote_config": remote_result,
                    "network_status": network_result,
                    "suggestions": self._generate_push_failure_suggestions(result),
                }

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_push_failure_suggestions(self, result: Dict[str, Any]) -> List[str]:
        """生成推送失败的建议"""
        suggestions = []
        stderr = result.get("stderr", "").lower()
        error = result.get("error", "").lower()

        if "connection" in stderr or "reset" in stderr:
            suggestions.append("网络连接不稳定，建议：")
            suggestions.append("1. 使用SSH替代HTTPS（已配置）")
            suggestions.append("2. 检查防火墙设置")
            suggestions.append("3. 尝试使用代理或VPN")
            suggestions.append("4. 等待网络稳定后重试")

        if "permission" in stderr or "denied" in stderr:
            suggestions.append("权限问题，建议：")
            suggestions.append("1. 确保SSH密钥已添加到GitHub")
            suggestions.append("2. 检查SSH密钥权限（chmod 600 ~/.ssh/id_*）")
            suggestions.append("3. 重启SSH代理（eval `ssh-agent` && ssh-add）")

        if "timeout" in stderr or "timeout" in error:
            suggestions.append("连接超时，建议：")
            suggestions.append("1. 增加超时时间")
            suggestions.append("2. 检查网络延迟")
            suggestions.append("3. 尝试在非高峰时段操作")

        if not suggestions:
            suggestions.append("未知错误，请检查错误信息")

        return suggestions

    def _handle_ssh_fix_host_key(self, host: str = "github.com", key_types: List[str] = None) -> Dict[str, Any]:
        """修复SSH主机密钥验证问题"""
        if key_types is None:
            key_types = ["rsa", "ecdsa", "ed25519"]

        try:
            # 确保SSH目录存在
            self.ssh_config_dir.mkdir(exist_ok=True, mode=0o700)

            known_hosts_file = self.ssh_config_dir / "known_hosts"
            results = []

            for key_type in key_types:
                try:
                    # 使用ssh-keyscan获取主机密钥
                    cmd = ["ssh-keyscan", "-t", key_type, host]
                    result = self._run_command(cmd, capture_output=True, timeout=10)

                    if result["success"] and result["stdout"]:
                        key_line = result["stdout"].strip()
                        # 解析密钥信息
                        if key_line and not key_line.startswith("#"):
                            # 追加到known_hosts文件
                            with open(known_hosts_file, "a", encoding="utf-8") as f:
                                f.write(f"{key_line}\n")

                            results.append(
                                {"key_type": key_type, "success": True, "key_line": key_line, "action": "added"}
                            )
                        else:
                            results.append(
                                {"key_type": key_type, "success": False, "error": f"未获取到有效的{key_type}密钥"}
                            )
                    else:
                        results.append(
                            {"key_type": key_type, "success": False, "error": result.get("error", "获取密钥失败")}
                        )
                except Exception as e:
                    results.append({"key_type": key_type, "success": False, "error": str(e)})

            # 统计成功情况
            success_count = sum(1 for r in results if r["success"])
            total_count = len(results)

            if success_count > 0:
                # 测试修复后的连接
                test_result = self._run_command(["ssh", "-T", f"git@{host}"], capture_output=True, timeout=10)

                return {
                    "success": True,
                    "host": host,
                    "keys_scanned": total_count,
                    "keys_added": success_count,
                    "results": results,
                    "test_after_fix": {
                        "success": test_result["success"],
                        "output": test_result.get("stdout", ""),
                        "error": test_result.get("stderr", ""),
                    },
                    "known_hosts_file": str(known_hosts_file),
                    "file_exists": known_hosts_file.exists(),
                    "file_size": known_hosts_file.stat().st_size if known_hosts_file.exists() else 0,
                    "instructions": "主机密钥已添加到known_hosts文件，现在可以尝试SSH连接",
                }
            else:
                return {
                    "success": False,
                    "host": host,
                    "results": results,
                    "error": "未能成功获取任何主机密钥，请检查网络连接",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_ssh_get_public_key(self, key_file: str = "id_ed25519") -> Dict[str, Any]:
        """获取SSH公钥内容"""
        try:
            # 确保有.pub扩展名
            if not key_file.endswith(".pub"):
                key_file = f"{key_file}.pub"

            public_key_path = self.ssh_config_dir / key_file
            if not public_key_path.exists():
                return {"success": False, "error": f"公钥文件不存在: {public_key_path}"}

            with open(public_key_path, encoding="utf-8") as f:
                public_key_content = f.read().strip()

            # 解析公钥信息
            parts = public_key_content.split()
            key_type = parts[0] if len(parts) > 0 else "unknown"
            key_data = parts[1] if len(parts) > 1 else ""
            comment = parts[2] if len(parts) > 2 else ""

            return {
                "success": True,
                "file_path": str(public_key_path),
                "content": public_key_content,
                "key_type": key_type,
                "key_data_preview": key_data[:20] + "..." if len(key_data) > 20 else key_data,
                "comment": comment,
                "size": len(public_key_content),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_git_check_remote(self, remote_name: str = "origin") -> Dict[str, Any]:
        """检查Git远程配置"""
        try:
            # 获取远程URL
            url_result = self._run_git_command(["remote", "get-url", remote_name])

            # 获取远程详细信息
            verbose_result = self._run_git_command(["remote", "-v"])

            # 检查是否是SSH URL
            current_url = url_result["stdout"].strip() if url_result["success"] else ""
            is_ssh = current_url.startswith("git@") or "ssh://" in current_url
            is_https = "https://" in current_url

            return {
                "success": url_result["success"],
                "remote_name": remote_name,
                "url": current_url,
                "is_ssh": is_ssh,
                "is_https": is_https,
                "protocol": "ssh" if is_ssh else "https" if is_https else "unknown",
                "verbose_output": verbose_result["stdout"] if verbose_result["success"] else "",
                "recommendation": "已使用SSH协议（推荐）" if is_ssh else "建议切换到SSH协议以获得更稳定的连接",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局SSH增强 MCP Server实例
_ssh_mcp_server: Optional[SSHEnhancedMCPServer] = None


def get_ssh_mcp_server(repo_path: Optional[str] = None) -> SSHEnhancedMCPServer:
    """获取全局SSH增强MCP服务器"""
    global _ssh_mcp_server
    if _ssh_mcp_server is None:
        _ssh_mcp_server = SSHEnhancedMCPServer(repo_path)
    return _ssh_mcp_server
