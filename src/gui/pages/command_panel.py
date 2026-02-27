"""
命令面板 - 快速执行CLI命令
"""

import subprocess  # 性能优化：模块级别导入

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class CommandPanel(QWidget):
    """命令面板 - 快速执行命令"""

    # 信号
    command_executed = Signal(str, int)  # command, return_code

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("⚡ 命令面板")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # 命令输入
        input_group = QGroupBox("执行命令")
        input_layout = QHBoxLayout()

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("输入命令 (如: cae-cli learn list)")
        self.cmd_input.setFont(QFont("Consolas", 11))
        self.cmd_input.returnPressed.connect(self._execute_command)
        input_layout.addWidget(self.cmd_input, 1)

        self.exec_btn = QPushButton("执行")
        self.exec_btn.clicked.connect(self._execute_command)
        self.exec_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        input_layout.addWidget(self.exec_btn)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 常用命令
        presets_group = QGroupBox("常用命令")
        presets_layout = QVBoxLayout()

        presets = [
            ("查看课程", "cae-cli learn list"),
            ("材料查询", "cae-cli material Q235"),
            ("版本信息", "cae-cli version"),
            ("系统信息", "cae-cli info"),
        ]

        for name, cmd in presets:
            btn = QPushButton(f"{name}: {cmd}")
            btn.clicked.connect(lambda checked, c=cmd: self._run_preset(c))
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
            """)
            presets_layout.addWidget(btn)

        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)

        # 输出区域
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setFont(QFont("Consolas", 10))
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
            }
        """)
        output_layout.addWidget(self.output)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group, 1)

    def _execute_command(self):
        """执行命令"""
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        self.output.append(f"\n$ {cmd}")
        self.output.append("-" * 40)

        # 使用 subprocess 执行

        try:
            # 检测是否以 cae-cli 开头
            if not cmd.startswith("cae-cli"):
                cmd = "cae-cli " + cmd

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
            )

            if result.stdout:
                self.output.append(result.stdout)
            if result.stderr:
                self.output.append(f"[stderr] {result.stderr}")

            self.output.append(f"\n[Exit code: {result.returncode}]")
            self.command_executed.emit(cmd, result.returncode)

        except subprocess.TimeoutExpired:
            self.output.append("[Error] 命令执行超时")
        except Exception as e:
            self.output.append(f"[Error] {str(e)}")

        # 滚动到底部
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def _run_preset(self, cmd: str):
        """运行预设命令"""
        self.cmd_input.setText(cmd)
        self._execute_command()
