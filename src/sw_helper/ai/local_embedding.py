#!/usr/bin/env python3
"""
本地嵌入模型加载器

使用 llama-cpp-python 加载本地 GGUF 嵌入模型
用于知识库向量检索
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class LocalEmbeddingModel:
    """本地嵌入模型管理器

    使用 llama-cpp-python 加载 GGUF 嵌入模型
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.llm = None
        self._model_loaded = False
        self._load_error = None

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """加载 GGUF 嵌入模型

        Args:
            model_path: 模型文件路径

        Returns:
            bool: 加载是否成功
        """
        if model_path:
            self.model_path = model_path

        if not self.model_path:
            print("错误: 未指定模型路径")
            return False

        model_file = Path(self.model_path)
        if not model_file.exists():
            print(f"错误: 模型文件不存在: {self.model_path}")
            return False

        try:
            import io
            import sys

            # 临时抑制警告输出
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()

            from llama_cpp import Llama

            # 加载模型（用于嵌入）
            self.llm = Llama(
                model_path=str(model_file),
                embedding=True,
                n_ctx=512,
                n_threads=4,
                verbose=False,
            )

            # 恢复 stderr
            sys.stderr = old_stderr

            self._model_loaded = True
            print(f"✓ 嵌入模型加载成功: {model_file.name}")
            return True

        except ImportError:
            self._load_error = "请安装 llama-cpp-python"
            return False
        except Exception as e:
            self._load_error = str(e)
            return False

    def encode(self, text: str) -> List[float]:
        """将文本转换为嵌入向量

        Args:
            text: 输入文本

        Returns:
            List[float]: 嵌入向量
        """
        if not self._model_loaded or not self.llm:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        # 截断过长文本
        max_chars = 512 * 4  # 约 512 个 token
        if len(text) > max_chars:
            text = text[:max_chars]

        embedding = self.llm.create_embedding(text)
        return embedding["data"][0]["embedding"]

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为嵌入向量

        Args:
            texts: 输入文本列表

        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not self._model_loaded or not self.llm:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        embeddings = []
        for text in texts:
            emb = self.encode(text)
            embeddings.append(emb)

        return embeddings

    def compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（余弦相似度）

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            float: 相似度 (0-1)
        """
        import math

        emb1 = self.encode(text1)
        emb2 = self.encode(text2)

        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        magnitude1 = math.sqrt(sum(a * a for a in emb1))
        magnitude2 = math.sqrt(sum(b * b for b in emb2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# 获取可执行文件或脚本所在目录
def _get_app_dir() -> Path:
    """获取应用所在目录（支持打包后的 exe）"""
    if getattr(sys, "frozen", False):
        # 打包后的 exe
        return Path(sys._MEIPASS)
    else:
        # 开发环境
        return Path(__file__).parent.parent.parent.parent


# 默认模型路径 - 先从 exe 同目录查找，再从应用目录查找
def _get_default_embedding_model() -> Optional[Path]:
    """获取默认嵌入模型路径"""
    app_dir = _get_app_dir()

    # 优先查找 exe/model 目录，然后是应用根目录
    for search_dir in [app_dir.parent, app_dir]:
        model_path = search_dir / "bge-m3-Q8_0.gguf"
        if model_path.exists():
            return model_path
    return None


DEFAULT_EMBEDDING_MODEL = _get_default_embedding_model()

# 全局单例
_embedding_model: Optional[LocalEmbeddingModel] = None


def get_embedding_model(model_path: Optional[str] = None) -> LocalEmbeddingModel:
    """获取嵌入模型单例

    Args:
        model_path: 模型路径，默认使用项目根目录的 bge-m3-Q8_0.gguf

    Returns:
        LocalEmbeddingModel: 嵌入模型实例
    """
    global _embedding_model

    if _embedding_model is None:
        # 默认路径
        if model_path is None and DEFAULT_EMBEDDING_MODEL.exists():
            model_path = str(DEFAULT_EMBEDDING_MODEL)

        _embedding_model = LocalEmbeddingModel(model_path)

        # 自动加载
        if model_path:
            _embedding_model.load_model(model_path)

    return _embedding_model


def search_knowledge(
    query: str,
    knowledge_dir: str,
    model_path: Optional[str] = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """搜索知识库

    Args:
        query: 查询文本
        knowledge_dir: 知识库目录
        model_path: 嵌入模型路径
        top_k: 返回结果数量

    Returns:
        List[Dict[str, Any]]: 搜索结果列表
    """
    # 获取嵌入模型
    embed_model = get_embedding_model(model_path)

    if not embed_model._model_loaded:
        return []

    # 获取查询的嵌入
    query_embedding = embed_model.encode(query)

    # 读取知识库文件
    knowledge_path = Path(knowledge_dir)
    if not knowledge_path.exists():
        return []

    # 收集所有文本
    documents = []
    for md_file in knowledge_path.glob("**/*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            # 简单分块：按段落分割
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if len(para) > 20:  # 忽略太短的段落
                    documents.append(
                        {
                            "source": str(md_file.relative_to(knowledge_path)),
                            "content": para,
                        }
                    )
        except Exception:
            continue

    if not documents:
        return []

    # 批量计算嵌入
    texts = [doc["content"] for doc in documents]
    embeddings = embed_model.encode_batch(texts)

    # 计算相似度
    results = []
    for i, doc in enumerate(documents):
        emb = embeddings[i]

        # 余弦相似度
        dot_product = sum(a * b for a, b in zip(query_embedding, emb))
        query_mag = sum(a * a for a in query_embedding) ** 0.5
        doc_mag = sum(b * b for b in emb) ** 0.5

        if query_mag > 0 and doc_mag > 0:
            similarity = dot_product / (query_mag * doc_mag)
            results.append(
                {
                    "content": doc["content"],
                    "source": doc["source"],
                    "score": similarity,
                }
            )

    # 排序并返回 top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    # 测试
    import sys

    # 检查模型文件
    if DEFAULT_EMBEDDING_MODEL.exists():
        print(f"找到嵌入模型: {DEFAULT_EMBEDDING_MODEL}")

        model = get_embedding_model()
        if model._model_loaded:
            # 测试嵌入
            test_text = "什么是应力"
            emb = model.encode(test_text)
            print(f"嵌入维度: {len(emb)}")
            print("嵌入测试成功!")

            # 测试知识库搜索
            knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
            if knowledge_dir.exists():
                results = search_knowledge("什么是有限元", str(knowledge_dir))
                print(f"\n搜索结果 ({len(results)}条):")
                for r in results:
                    print(f"  - {r['source']} (相似度: {r['score']:.3f})")
                    print(f"    {r['content'][:100]}...")
    else:
        print(f"未找到嵌入模型: {DEFAULT_EMBEDDING_MODEL}")
        print("请将 bge-m3-Q8_0.gguf 放到项目根目录")
