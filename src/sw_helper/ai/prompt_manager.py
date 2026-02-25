"""
提示词管理器
动态加载和管理AI提示词
"""

from pathlib import Path
from typing import Dict, Optional, List

# 提示词目录 - 在项目根目录的prompts文件夹
PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"


class PromptManager:
    """提示词管理器"""

    # 提示词缓存
    _cache: Dict[str, str] = {}

    @classmethod
    def get_prompt(cls, category: str, name: str) -> str:
        """获取指定提示词

        Args:
            category: 分类 (system/learning/lifestyle/mechanical)
            name: 提示词文件名

        Returns:
            str: 提示词内容
        """
        key = f"{category}/{name}"

        # 检查缓存
        if key in cls._cache:
            return cls._cache[key]

        # 加载文件
        prompt_file = PROMPTS_DIR / category / f"{name}.md"
        if not prompt_file.exists():
            return f"提示词文件不存在: {prompt_file}"

        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 缓存
            cls._cache[key] = content
            return content

        except Exception as e:
            return f"读取提示词失败: {e}"

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """获取所有分类"""
        categories = []
        for item in PROMPTS_DIR.iterdir():
            if item.is_dir():
                categories.append(item.name)
        return sorted(categories)

    @classmethod
    def get_prompts_in_category(cls, category: str) -> List[str]:
        """获取分类下的所有提示词"""
        category_dir = PROMPTS_DIR / category
        if not category_dir.exists():
            return []

        prompts = []
        for f in category_dir.glob("*.md"):
            prompts.append(f.stem)
        return sorted(prompts)

    @classmethod
    def list_all_prompts(cls) -> Dict[str, List[str]]:
        """列出所有提示词"""
        result = {}
        for category in cls.get_all_categories():
            result[category] = cls.get_prompts_in_category(category)
        return result

    @classmethod
    def build_system_prompt(cls, mode: str = "default") -> str:
        """构建系统提示词

        Args:
            mode: 模式 (default/learning/lifestyle/mechanical)

        Returns:
            str: 完整的系统提示词
        """
        # 基础提示词
        system_prompt = cls.get_prompt("system", "main")

        # 根据模式添加特定提示词
        if mode == "learning":
            system_prompt += "\n\n" + cls.get_prompt("learning", "3-2-1-method")
            system_prompt += "\n\n" + cls.get_prompt("learning", "feynman")
        elif mode == "lifestyle":
            system_prompt += "\n\n" + cls.get_prompt("lifestyle", "mindset")
        elif mode == "mechanical":
            system_prompt += "\n\n" + cls.get_prompt("mechanical", "cad-design")

        return system_prompt

    @classmethod
    def refresh_cache(cls):
        """刷新缓存"""
        cls._cache.clear()


def get_prompt(category: str, name: str) -> str:
    """获取提示词的便捷函数"""
    return PromptManager.get_prompt(category, name)


def list_prompts() -> Dict[str, List[str]]:
    """列出所有提示词"""
    return PromptManager.list_all_prompts()
