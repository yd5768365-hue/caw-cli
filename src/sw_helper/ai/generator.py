"""
AI集成模块 - 支持几何生成和优化建议
"""

from typing import Any, Dict, List, Optional


class AIGenerator:
    """AI几何生成器 - 基于LLM的几何描述生成"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider = None
        self._setup_provider()

    def _setup_provider(self):
        """设置AI提供商"""
        # 检查环境变量或配置文件
        import os

        # 优先使用传入的api_key
        if self.api_key:
            return

        # 尝试从环境变量获取
        providers = {
            "OPENAI_API_KEY": "openai",
            "ANTHROPIC_API_KEY": "anthropic",
            "GEMINI_API_KEY": "google",
            "DEEPSEEK_API_KEY": "deepseek",
        }

        for env_var, provider in providers.items():
            if os.getenv(env_var):
                self.api_key = os.getenv(env_var)
                self.provider = provider
                break

    def generate_geometry_prompt(self, description: str, constraints: Optional[Dict] = None) -> str:
        """生成几何结构的提示词

        Args:
            description: 自然语言描述，如"带圆角的立方体，边长100mm，圆角R5"
            constraints: 约束条件

        Returns:
            结构化提示词
        """
        prompt = f"""你是一个CAD几何设计专家。请根据以下描述生成参数化的几何结构定义。

描述: {description}

请生成以下格式的JSON响应:
{{
    "type": "几何类型(如: cube, cylinder, bracket, shell)",
    "parameters": {{
        "参数名": {{"value": 值, "unit": "单位", "description": "描述", "modifiable": true/false}}
    }},
    "features": [
        {{"type": "特征类型", "parameters": {{}}}}
    ],
    "material": "建议材料",
    "manufacturing_notes": ["制造注意事项"],
    "optimization_hints": ["优化建议"]
}}

要求:
1. 所有尺寸参数必须是可修改的
2. 考虑制造可行性
3. 包含工程最佳实践
4. 标注关键尺寸和公差
"""
        return prompt

    def parse_geometry_description(self, description: str) -> Dict[str, Any]:
        """解析几何描述并返回结构化数据

        这里可以实现与真实AI API的集成，现在返回模拟数据
        """
        # TODO: 集成真实的AI API调用
        # 模拟返回一个带圆角立方体的结构
        return {
            "type": "cube_with_fillet",
            "parameters": {
                "length": {
                    "value": 100,
                    "unit": "mm",
                    "description": "长度",
                    "modifiable": True,
                    "range": [50, 200],
                },
                "width": {
                    "value": 80,
                    "unit": "mm",
                    "description": "宽度",
                    "modifiable": True,
                    "range": [40, 160],
                },
                "height": {
                    "value": 60,
                    "unit": "mm",
                    "description": "高度",
                    "modifiable": True,
                    "range": [30, 120],
                },
                "fillet_radius": {
                    "value": 5,
                    "unit": "mm",
                    "description": "圆角半径",
                    "modifiable": True,
                    "range": [1, 15],
                },
            },
            "features": [
                {"type": "extrude", "sketch": "rectangle", "depth": "height"},
                {"type": "fillet", "edges": "all_edges", "radius": "fillet_radius"},
            ],
            "material": "铝合金6061",
            "manufacturing_notes": [
                "建议CNC加工",
                "圆角处注意刀具半径补偿",
                "表面粗糙度Ra3.2",
            ],
            "optimization_hints": [
                "圆角半径增大可降低应力集中",
                "壁厚均匀有利于铸造",
                "考虑脱模斜度",
            ],
        }

    def generate_optimization_suggestions(
        self,
        current_params: Dict[str, Any],
        quality_metrics: Dict[str, Any],
        target: str = "strength",
        knowledge_text: str = "",
    ) -> List[Dict[str, Any]]:
        """基于当前参数和质量指标生成优化建议

        Args:
            current_params: 当前参数
            quality_metrics: 质量指标
            target: 优化目标 (strength, weight, cost, manufacturability)
            knowledge_text: 知识库内容，用于提供专业建议

        Returns:
            优化建议列表
        """
        suggestions = []

        # 基于质量指标生成建议
        if quality_metrics.get("max_stress", 0) > 200e6:  # 200MPa
            suggestions.append(
                {
                    "type": "increase_thickness",
                    "parameter": "wall_thickness",
                    "current": current_params.get("wall_thickness", 5),
                    "suggested": current_params.get("wall_thickness", 5) * 1.2,
                    "reason": "应力过高，建议增加壁厚",
                    "expected_improvement": "应力降低约15%",
                }
            )

        if quality_metrics.get("safety_factor", 2) < 1.5:
            suggestions.append(
                {
                    "type": "material_upgrade",
                    "current": current_params.get("material", "Q235"),
                    "suggested": "Q345",
                    "reason": "安全系数不足，建议升级材料",
                    "expected_improvement": "强度提升约47%",
                }
            )

        # 圆角优化
        if "fillet_radius" in current_params:
            suggestions.append(
                {
                    "type": "fillet_optimization",
                    "parameter": "fillet_radius",
                    "current": current_params["fillet_radius"],
                    "suggested": current_params["fillet_radius"] * 1.5,
                    "reason": "增大圆角可降低应力集中",
                    "expected_improvement": "应力集中系数降低",
                }
            )

        return suggestions

    def generate_design_variants(self, base_params: Dict[str, Any], num_variants: int = 3) -> List[Dict[str, Any]]:
        """生成设计变体

        Args:
            base_params: 基础参数
            num_variants: 变体数量

        Returns:
            设计变体列表
        """
        variants = []

        for i in range(num_variants):
            variant = {"id": i + 1, "name": f"变体 {i + 1}", "parameters": {}}

            # 生成参数变体
            for param_name, param_info in base_params.items():
                if isinstance(param_info, dict) and param_info.get("modifiable"):
                    current = param_info["value"]
                    variation = 0.1 * (i + 1)  # 10%, 20%, 30% 变化

                    # 根据奇偶决定增减
                    if i % 2 == 0:
                        new_value = current * (1 + variation)
                    else:
                        new_value = current * (1 - variation)

                    # 限制在范围内
                    min_val = param_info.get("range", [current * 0.5, current * 1.5])[0]
                    max_val = param_info.get("range", [current * 0.5, current * 1.5])[1]
                    new_value = max(min_val, min(max_val, new_value))

                    variant["parameters"][param_name] = {
                        **param_info,
                        "value": round(new_value, 2),
                    }
                else:
                    variant["parameters"][param_name] = param_info

            variants.append(variant)

        return variants


class DesignAssistant:
    """设计助手 - 提供交互式设计建议"""

    def __init__(self):
        self.ai_generator = AIGenerator()
        self.conversation_history = []

    def ask(self, question: str, context: Optional[Dict] = None) -> str:
        """问答式交互设计

        Args:
            question: 用户问题
            context: 当前设计上下文

        Returns:
            AI回答
        """
        # 记录对话
        self.conversation_history.append({"role": "user", "content": question})

        # 模拟AI回答（实际实现应调用API）
        responses = {
            "圆角": "圆角半径建议取壁厚的0.5-1倍，既能降低应力集中又不过度削弱结构。",
            "材料": "对于承重结构，建议选择Q345或更高强度的材料。",
            "网格": "建议关键区域网格尺寸不大于2mm，圆角处局部加密。",
        }

        # 简单关键词匹配
        answer = "这是一个很好的问题。根据工程经验，我建议：\n\n"

        for keyword, response in responses.items():
            if keyword in question:
                answer += f"• {response}\n"

        if answer == "这是一个很好的问题。根据工程经验，我建议：\n\n":
            answer += "• 请提供更具体的设计参数，我可以给出更准确的建议。\n"
            answer += "• 建议先进行静力分析，评估当前设计的安全性。\n"
            answer += "• 考虑制造工艺限制，确保设计可制造。\n"

        self.conversation_history.append({"role": "assistant", "content": answer})

        return answer

    def generate_design_report(self, design_data: Dict[str, Any]) -> str:
        """生成设计报告

        Args:
            design_data: 设计数据

        Returns:
            报告文本
        """
        report = f"""# 设计分析报告

## 设计概述
- 类型: {design_data.get("type", "未知")}
- 材料: {design_data.get("material", "未指定")}

## 关键参数
"""

        for param_name, param_info in design_data.get("parameters", {}).items():
            report += f"- {param_info.get('description', param_name)}: {param_info.get('value')} {param_info.get('unit', '')}\n"

        report += "\n## 制造建议\n"
        for note in design_data.get("manufacturing_notes", []):
            report += f"- {note}\n"

        report += "\n## 优化建议\n"
        for hint in design_data.get("optimization_hints", []):
            report += f"- {hint}\n"

        return report
