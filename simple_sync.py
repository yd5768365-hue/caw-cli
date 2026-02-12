#!/usr/bin/env python3
"""
简单但稳健的项目同步脚本
使用直接git命令，增加重试机制和网络检查
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import socket


def run_command(cmd, cwd=None, timeout=30, retries=3):
    """运行命令，支持重试"""
    for attempt in range(retries):
        try:
            print(f"尝试 {attempt + 1}/{retries}: {cmd}")
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout,
                shell=True
            )

            if result.returncode == 0:
                print(f"  成功: {result.stdout[:100] if result.stdout else '无输出'}")
                return result
            else:
                print(f"  失败 (尝试 {attempt + 1}): {result.stderr[:200] if result.stderr else '未知错误'}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"  等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    return result

        except subprocess.TimeoutExpired:
            print(f"  超时 (尝试 {attempt + 1})")
            if attempt < retries - 1:
                print(f"  等待 5 秒后重试...")
                time.sleep(5)
            else:
                return subprocess.CompletedProcess(cmd, 1, "", "命令执行超时")
        except Exception as e:
            print(f"  异常 (尝试 {attempt + 1}): {str(e)[:200]}")
            if attempt < retries - 1:
                time.sleep(2)

    return subprocess.CompletedProcess(cmd, 1, "", "所有重试均失败")


def check_network(hosts=None):
    """检查网络连接"""
    if hosts is None:
        hosts = ["github.com", "8.8.8.8", "google.com"]

    print("检查网络连接...")
    for host in hosts:
        try:
            # 尝试解析域名
            socket.gethostbyname(host)
            print(f"  [OK] {host}: 域名解析成功")

            # 尝试连接常用端口
            for port in [80, 443]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    if result == 0:
                        print(f"    - 端口 {port}: 可达")
                    else:
                        print(f"    - 端口 {port}: 不可达")
                except:
                    print(f"    - 端口 {port}: 连接失败")

        except socket.gaierror:
            print(f"  [FAIL] {host}: 域名解析失败")
        except Exception as e:
            print(f"  [FAIL] {host}: 连接失败 - {str(e)[:50]}")

    print()


def check_ssh_setup():
    """检查SSH设置"""
    print("检查SSH设置...")

    # 检查SSH目录
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        print(f"  [OK] SSH目录存在: {ssh_dir}")

        # 检查常见密钥文件
        key_files = ["id_rsa", "id_ed25519", "id_ecdsa"]
        found_keys = []
        for key in key_files:
            private = ssh_dir / key
            public = ssh_dir / f"{key}.pub"
            if private.exists():
                found_keys.append(key)
                print(f"    - {key}: 找到私钥")
                if public.exists():
                    print(f"      - 找到公钥")

        if found_keys:
            print(f"  [OK] 找到 {len(found_keys)} 个SSH密钥")
        else:
            print(f"  [FAIL] 未找到SSH密钥文件")
    else:
        print(f"  [FAIL] SSH目录不存在: {ssh_dir}")

    print()


def sync_project():
    """同步项目"""
    print("=" * 70)
    print("简单但稳健的项目同步")
    print("=" * 70)

    # 检查是否在git仓库中
    repo_path = Path.cwd()
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print("错误: 当前目录不是Git仓库!")
        print(f"当前目录: {repo_path}")
        print("请在项目根目录运行此脚本")
        return False

    print(f"仓库: {repo_path}")

    # 1. 网络检查
    check_network()

    # 2. SSH检查
    check_ssh_setup()

    # 3. 检查远程配置
    print("检查Git远程配置...")
    remote_result = run_command("git remote -v", cwd=repo_path)
    if remote_result.returncode == 0:
        print(f"远程配置:\n{remote_result.stdout}")

    # 4. 查看状态
    print("\n1. 查看Git状态...")
    status_result = run_command("git status", cwd=repo_path)
    if status_result.returncode != 0:
        print("无法获取Git状态")
        return False

    # 5. 添加所有更改
    print("\n2. 添加所有更改的文件...")
    # 先查看具体更改
    diff_result = run_command("git diff --name-only", cwd=repo_path)
    if diff_result.returncode == 0 and diff_result.stdout.strip():
        changed_files = diff_result.stdout.strip().split('\n')
        print(f"检测到 {len(changed_files)} 个更改的文件:")
        for file in changed_files[:10]:  # 只显示前10个
            print(f"  - {file}")
        if len(changed_files) > 10:
            print(f"  ... 还有 {len(changed_files) - 10} 个文件")

    add_result = run_command("git add .", cwd=repo_path, retries=2)
    if add_result.returncode != 0:
        print("添加文件失败，尝试添加特定文件...")
        # 尝试逐个添加
        if 'changed_files' in locals():
            for file in changed_files:
                file_result = run_command(f"git add \"{file}\"", cwd=repo_path, retries=1)
                if file_result.returncode != 0:
                    print(f"  无法添加: {file}")

    # 6. 创建提交
    print("\n3. 创建提交...")
    commit_message = """更新项目配置和SSH增强功能

- 新增SSH增强的MCP服务器模块
- 添加paramiko作为可选依赖（SSH功能）
- 更新项目配置文件(pyproject.toml)
- 新增简单同步脚本，提供更稳定的同步方案
- 修复MCP服务器导入配置

[机器人] 通过简单同步脚本自动同步"""

    commit_result = run_command(f'git commit -m "{commit_message}"', cwd=repo_path)
    if commit_result.returncode != 0:
        print("提交失败，尝试检查是否有需要提交的更改...")
        status_check = run_command("git status --porcelain", cwd=repo_path)
        if status_check.stdout.strip():
            print("仍有未提交的更改，但提交失败")
            print(f"状态: {status_check.stdout}")
            return False
        else:
            print("没有需要提交的更改")
            return True

    # 7. 推送更改（使用不同策略）
    print("\n4. 推送更改到远程仓库...")

    # 策略1: 直接推送（主策略）
    print("策略1: 直接推送...")
    push_result = run_command("git push origin main", cwd=repo_path, timeout=60, retries=3)

    if push_result.returncode == 0:
        print("[OK] 推送成功!")
    else:
        print("[FAIL] 直接推送失败，尝试备选策略...")

        # 策略2: 使用更详细的输出
        print("策略2: 使用详细输出推送...")
        push_result2 = run_command("git push -v origin main", cwd=repo_path, timeout=90, retries=2)

        if push_result2.returncode == 0:
            print("[OK] 详细推送成功!")
        else:
            print("[FAIL] 详细推送失败...")

            # 策略3: 强制推送（谨慎使用）
            print("策略3: 检查是否需要强制推送...")
            print("注意: 强制推送可能会覆盖远程更改，请谨慎使用")

            # 先拉取最新更改
            print("  先拉取最新更改...")
            pull_result = run_command("git pull origin main", cwd=repo_path, timeout=60, retries=2)

            if pull_result.returncode == 0:
                print("  [OK] 拉取成功，重新尝试推送...")
                push_result3 = run_command("git push origin main", cwd=repo_path, timeout=60, retries=2)

                if push_result3.returncode == 0:
                    print("[OK] 重新推送成功!")
                else:
                    print("[FAIL] 重新推送失败")
                    return False
            else:
                print("  [FAIL] 拉取失败")
                return False

    # 8. 查看结果
    print("\n5. 查看结果...")

    # 查看最近提交
    log_result = run_command("git log --oneline -3", cwd=repo_path)
    if log_result.returncode == 0:
        print("最近提交:")
        print(log_result.stdout)

    # 查看远程状态
    remote_status = run_command("git remote show origin", cwd=repo_path)
    if remote_status.returncode == 0:
        print("远程状态:")
        print(remote_status.stdout)

    print("\n" + "=" * 70)
    print("同步完成!")
    print("=" * 70)
    print(f"\n总结:")
    print(f"- 仓库: {repo_path}")
    print(f"- 提交: {commit_message.splitlines()[0]}")
    print(f"- 推送: {'成功' if push_result.returncode == 0 else '部分成功'}")
    print(f"- 远程: origin/main")
    print(f"- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return True


if __name__ == "__main__":
    try:
        success = sync_project()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n同步被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n同步过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)