#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG (Retrieval-Augmented Generation) Engine for CAE-CLI学习模式
使用 ChromaDB + sentence-transformers 实现向量检索
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
import os
import sys
import traceback
import sqlite3
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class RAGCacheManager:
    """RAG查询缓存管理器 - 基于SQLite的本地缓存"""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录，默认 ~/.cae-cli/cache
        """
        if cache_dir is None:
            home = Path.home()
            self.cache_dir = home / ".cae-cli" / "cache"
        else:
            self.cache_dir = Path(cache_dir)

        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "rag.db"
        self._init_database()

    def _init_database(self):
        """初始化SQLite数据库表 - 简化结构"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 创建缓存表（简化版）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_cache (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expire_at TIMESTAMP NOT NULL
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expire_at
            ON rag_cache(expire_at)
        """)

        conn.commit()
        conn.close()

    def _compute_knowledge_hash(self, knowledge_dir: Path, src_dir: Optional[Path] = None) -> str:
        """
        计算知识库目录的哈希值

        Args:
            knowledge_dir: knowledge目录路径
            src_dir: src核心模块目录路径（可选）

        Returns:
            基于文件修改时间和文件大小的哈希字符串
        """
        hash_data = []

        # 1. 计算knowledge/目录的哈希
        if knowledge_dir.exists():
            for md_file in knowledge_dir.glob("*.md"):
                if md_file.is_file():
                    stat = md_file.stat()
                    # 使用文件路径、修改时间和大小
                    file_info = f"{md_file}:{stat.st_mtime}:{stat.st_size}"
                    hash_data.append(file_info)

        # 2. 计算src/核心模块的哈希（只包含.py文件）
        if src_dir and src_dir.exists():
            # 定义核心模块路径模式
            core_patterns = [
                "sw_helper/geometry/**/*.py",
                "sw_helper/mesh/**/*.py",
                "sw_helper/material/**/*.py",
                "sw_helper/mechanics/**/*.py",
                "sw_helper/report/**/*.py",
                "sw_helper/utils/**/*.py"
            ]

            for pattern in core_patterns:
                for py_file in src_dir.glob(pattern):
                    if py_file.is_file():
                        try:
                            stat = py_file.stat()
                            file_info = f"{py_file}:{stat.st_mtime}:{stat.st_size}"
                            hash_data.append(file_info)
                        except:
                            pass

        # 如果没有文件，返回默认哈希
        if not hash_data:
            return "empty_knowledge_base"

        # 排序以确保一致性
        hash_data.sort()
        combined = "|".join(hash_data)
        return hashlib.md5(combined.encode()).hexdigest()

    def _generate_query_hash(self, query: str, top_k: int = 3, max_length: int = 0) -> str:
        """生成查询哈希（包含所有影响结果的参数）"""
        data = f"{query}|{top_k}|{max_length}"
        return hashlib.md5(data.encode()).hexdigest()

    def get_cache(self, query: str, top_k: int = 3, max_length: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        从缓存获取查询结果

        Args:
            query: 查询字符串
            top_k: 返回结果数量
            max_length: 内容最大长度

        Returns:
            缓存的检索结果列表，如果未命中或过期则返回None
        """
        query_hash = self._generate_query_hash(query, top_k, max_length)

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # 查询缓存（检查是否过期）
            cursor.execute("""
                SELECT result_json, created_at
                FROM rag_cache
                WHERE query_hash = ? AND expire_at > datetime('now')
            """, (query_hash,))

            row = cursor.fetchone()
            if row:
                # 更新访问时间（可选）
                cursor.execute("""
                    UPDATE rag_cache
                    SET created_at = CURRENT_TIMESTAMP
                    WHERE query_hash = ?
                """, (query_hash,))
                conn.commit()

                # 返回缓存的JSON结果
                result_json = row["result_json"]
                return json.loads(result_json)

            return None

        finally:
            conn.close()

    def set_cache(self, query: str, results: List[Dict[str, Any]], top_k: int = 3, max_length: int = 0, ttl_hours: int = 24):
        """
        设置缓存

        Args:
            query: 查询字符串
            results: 检索结果列表
            top_k: 返回结果数量
            max_length: 内容最大长度
            ttl_hours: 缓存有效期（小时）
        """
        query_hash = self._generate_query_hash(query, top_k, max_length)
        result_json = json.dumps(results, ensure_ascii=False)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            # 计算过期时间
            from datetime import datetime, timedelta
            expire_at = datetime.now() + timedelta(hours=ttl_hours)
            expire_str = expire_at.isoformat()

            # 插入或替换缓存
            cursor.execute("""
                INSERT OR REPLACE INTO rag_cache
                (query_hash, query_text, result_json, created_at, expire_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (query_hash, query, result_json, expire_str))

            conn.commit()

        finally:
            conn.close()

    def cleanup_expired(self):
        """清理过期的缓存条目（基于expire_at字段）"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM rag_cache
                WHERE expire_at <= datetime('now')
            """)

            deleted_count = cursor.rowcount
            conn.commit()

            if deleted_count > 0:
                print(f"[RAG缓存] 清理了 {deleted_count} 个过期条目")

        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) as total FROM rag_cache")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) as active FROM rag_cache
                WHERE expire_at > datetime('now')
            """)
            active = cursor.fetchone()["active"]

            cursor.execute("""
                SELECT COUNT(*) as expired FROM rag_cache
                WHERE expire_at <= datetime('now')
            """)
            expired = cursor.fetchone()["expired"]

            # 计算缓存命中率（需要额外跟踪，暂时返回0）
            hit_rate = 0.0

            return {
                "total_entries": total,
                "active_entries": active,
                "expired_entries": expired,
                "hit_rate": hit_rate,
                "db_path": str(self.db_path)
            }

        finally:
            conn.close()


class RAGEngine:
    def __init__(self, knowledge_dir="knowledge", model_path=None):
        """
        初始化RAG引擎

        Args:
            knowledge_dir: 知识库目录，默认在项目根目录的 knowledge 文件夹
            model_path: 可选的自定义模型路径，如果提供则使用本地模型文件
        """
        self.knowledge_dir = Path(knowledge_dir)

        # 确保knowledge目录存在
        if not self.knowledge_dir.exists():
            self.knowledge_dir.mkdir(exist_ok=True)
            print(f"创建知识库目录: {self.knowledge_dir}")

        # 尝试导入sentence-transformers，提供友好的错误提示
        try:
            from sentence_transformers import SentenceTransformer
            self.SentenceTransformer = SentenceTransformer
            self.sentence_transformers_available = True
        except ImportError as e:
            print(f"警告: 无法导入sentence-transformers: {e}")
            print("请安装: pip install sentence-transformers")
            self.sentence_transformers_available = False
            return

        # 初始化模型 - 使用小模型减少内存占用
        try:
            import os
            # 检查环境变量中的模型路径
            env_model_path = os.environ.get('CAE_CLI_MODEL_PATH')
            if env_model_path and not model_path:
                model_path = env_model_path
                print(f"使用环境变量指定的模型路径: {model_path}")

            if model_path:
                # 使用自定义模型路径
                print(f"尝试加载本地模型: {model_path}")
                self.model = self.SentenceTransformer(model_path)
                print("[OK] 从自定义路径加载 sentence-transformers 模型")
            else:
                # 尝试从缓存加载，如果失败则尝试离线模式
                print("尝试加载默认模型 'all-MiniLM-L6-v2'...")
                try:
                    self.model = self.SentenceTransformer('all-MiniLM-L6-v2')
                    print("[OK] 加载 sentence-transformers 模型")
                except Exception as download_error:
                    print(f"模型下载失败: {download_error}")
                    print("尝试检查本地缓存...")
                    # 检查是否有本地缓存的模型

                    # HuggingFace默认缓存路径
                    cache_home = os.environ.get('HF_HOME', os.path.expanduser('~/.cache/huggingface'))
                    model_cache_path = Path(cache_home) / 'hub' / 'models--sentence-transformers--all-MiniLM-L6-v2'

                    if model_cache_path.exists():
                        print(f"找到本地缓存模型: {model_cache_path}")
                        try:
                            self.model = self.SentenceTransformer(str(model_cache_path))
                            print("[OK] 从缓存加载模型")
                        except Exception as cache_error:
                            print(f"从缓存加载失败: {cache_error}")
                            raise download_error
                    else:
                        raise download_error
        except Exception as e:
            print(f"警告: 加载sentence-transformers模型失败: {e}")
            print("可能的原因:")
            print("1. 网络连接问题，无法下载模型")
            print("2. 模型文件损坏或不完整")
            print("3. 磁盘空间不足")
            print("4. 权限问题")
            print("\n解决方案:")
            print("1. 检查网络连接")
            print("2. 手动下载模型: pip install sentence-transformers[all]")
            print("3. 指定本地模型路径: RAGEngine(model_path='本地路径')")
            self.sentence_transformers_available = False
            return

        # 初始化ChromaDB
        try:
            self.client = chromadb.Client(Settings(
                allow_reset=True,
                anonymized_telemetry=False,
                persist_directory=str(self.knowledge_dir / "chroma_db")
            ))
            print("[OK] 初始化 ChromaDB 客户端")
        except Exception as e:
            print(f"警告: 初始化ChromaDB失败: {e}")
            # 尝试回退到内存模式
            try:
                self.client = chromadb.Client(Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                ))
                print("[OK] 使用内存模式 ChromaDB")
            except Exception as e2:
                print(f"错误: 无法初始化ChromaDB: {e2}")
                self.sentence_transformers_available = False
                return

        # 获取或创建集合
        try:
            self.collection = self.client.get_or_create_collection(
                name="cae_knowledge",
                metadata={"description": "CAE-CLI机械专业知识库"}
            )
            print("[OK] 加载 ChromaDB 集合")
        except Exception as e:
            print(f"错误: 无法获取或创建集合: {e}")
            self.sentence_transformers_available = False
            return

        # 初始化缓存管理器
        self.cache_manager = RAGCacheManager()

        # 计算知识库哈希（基于knowledge目录和src核心模块）
        # 尝试自动发现src目录（假设在项目根目录下）
        project_root = self.knowledge_dir.parent
        src_dir = project_root / "src" if project_root.name else Path("src")

        self.knowledge_hash = self.cache_manager._compute_knowledge_hash(
            self.knowledge_dir,
            src_dir if src_dir.exists() else None
        )

        print(f"[缓存] 知识库哈希: {self.knowledge_hash[:12]}...")
        print(f"[缓存] 数据库路径: {self.cache_manager.db_path}")

        # 定期清理过期缓存（24小时TTL）
        self.cache_manager.cleanup_expired(ttl_hours=24)

        # 加载知识库
        self._load_knowledge()

    def _load_knowledge(self):
        """把 knowledge/ 目录的 md 文件全部向量化"""
        if not self.sentence_transformers_available:
            return

        # 检查是否已经有数据
        try:
            count = self.collection.count()
            if count > 0:
                print(f"知识库已有 {count} 个文档，跳过加载")
                return
        except:
            pass

        documents = []
        metadatas = []
        ids = []

        # 查找所有Markdown文件
        md_files = list(self.knowledge_dir.glob("*.md"))
        if not md_files:
            print(f"警告: 知识库目录 '{self.knowledge_dir}' 中没有找到 Markdown 文件")
            # 创建示例知识文件
            self._create_sample_knowledge()
            md_files = list(self.knowledge_dir.glob("*.md"))

        print(f"找到 {len(md_files)} 个知识文件，正在向量化...")

        for file in md_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 跳过空文件
                if not content.strip():
                    continue

                documents.append(content)
                metadatas.append({"source": file.name, "path": str(file)})
                ids.append(file.stem)

            except Exception as e:
                print(f"警告: 无法读取文件 {file}: {e}")

        if not documents:
            print("警告: 没有可用的文档内容")
            return

        try:
            # 生成嵌入向量
            embeddings = self.model.encode(documents, show_progress_bar=True, normalize_embeddings=True).tolist()

            # 添加到集合
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            print(f"[OK] 已加载 {len(documents)} 个知识文档到向量数据库")

        except Exception as e:
            print(f"错误: 向量化或添加文档失败: {e}")
            print(traceback.format_exc())

    def _create_sample_knowledge(self):
        """创建示例知识文件（如果目录为空）"""
        sample_content = """# 常用材料属性

## 钢材料

### Q235
- **屈服强度**: 235 MPa
- **抗拉强度**: 370-500 MPa
- **伸长率**: 26%
- **用途**: 普通结构钢，用于建筑、桥梁等

### 45钢
- **屈服强度**: 355 MPa
- **抗拉强度**: 600 MPa
- **伸长率**: 16%
- **用途**: 中碳结构钢，用于轴、齿轮等

### Q345
- **屈服强度**: 345 MPa
- **抗拉强度**: 470-630 MPa
- **伸长率**: 22%
- **用途**: 低合金高强度钢，用于压力容器、船舶等

## 铝合金

### 6061
- **屈服强度**: 55 MPa
- **抗拉强度**: 180 MPa
- **伸长率**: 10%
- **用途**: 通用铝合金，用于航空、汽车、建筑等

### 7075
- **屈服强度**: 505 MPa
- **抗拉强度**: 570 MPa
- **伸长率**: 11%
- **用途**: 高强度铝合金，用于航空航天领域

## 紧固件

### 螺栓规格
- **M6**: 螺距1.0mm，头高3.5mm，头宽10.0mm
- **M8**: 螺距1.25mm，头高4.0mm，头宽13.0mm
- **M10**: 螺距1.5mm，头高4.8mm，头宽16.0mm
- **M12**: 螺距1.75mm，头高5.5mm，头宽18.0mm

### 螺栓强度等级
- **4.8级**: 最小抗拉强度400MPa，最小屈服强度320MPa，普通螺栓
- **8.8级**: 最小抗拉强度800MPa，最小屈服强度640MPa，高强度螺栓
- **10.9级**: 最小抗拉强度1000MPa，最小屈服强度900MPa，高强度螺栓
- **12.9级**: 最小抗拉强度1200MPa，最小屈服强度1080MPa，超高强度螺栓

## 公差配合

### 常用公差等级
- **IT1-IT4**: 高精度量仪、精密机械等，如量块、千分尺
- **IT5-IT6**: 高精度配合，如机床主轴与轴承
- **IT7-IT8**: 中等精度配合，如齿轮、联轴器
- **IT9-IT10**: 低精度配合，如支架、外壳
- **IT11-IT13**: 粗糙配合，如农业机械、建筑机械

### 配合类型
- **间隙配合**: 孔的尺寸大于轴的尺寸，有间隙，用于滑动轴承、齿轮啮合等
- **过盈配合**: 孔的尺寸小于轴的尺寸，有过盈，用于轴与轮毂的连接等
- **过渡配合**: 可能有间隙或过盈，配合较紧，用于定位配合、定心配合等
"""

        sample_file = self.knowledge_dir / "sample_knowledge.md"
        try:
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"[OK] 已创建示例知识文件: {sample_file}")
        except Exception as e:
            print(f"错误: 无法创建示例文件: {e}")

    def search(self, query: str, top_k: int = 3, max_length: int = 0) -> list:
        """
        检索最相关的知识片段（带缓存）

        Args:
            query: 查询文本
            top_k: 返回的结果数量
            max_length: 内容最大长度（字符数），0表示不截断

        Returns:
            检索结果列表，每个结果包含 content、source、distance 字段
        """
        import time
        start_time = time.time()

        if not self.sentence_transformers_available:
            print("错误: sentence-transformers不可用")
            return []

        if not query or not query.strip():
            return []

        try:
            # 1. 先尝试从缓存获取
            cached_results = self.cache_manager.get_cache(query, top_k, max_length)
            if cached_results is not None:
                elapsed_ms = int((time.time() - start_time) * 1000)
                # 估算节省的tokens：假设一次向量编码相当于50个tokens
                saved_tokens = 50
                print(f"[RAG] 缓存命中 | 耗时 {elapsed_ms}ms | 节省 tokens {saved_tokens}")
                return cached_results

            # 2. 缓存未命中，执行向量检索
            # 生成查询向量
            query_embedding = self.model.encode(query, normalize_embeddings=True).tolist()

            # 查询向量数据库
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, 5),  # 限制最多5个结果
                include=["documents", "metadatas", "distances"]
            )

            # 格式化结果
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, meta, dist) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # 内容截断处理
                    content = doc
                    if max_length > 0 and len(content) > max_length:
                        # 尝试截断到最近的句号、感叹号、问号或换行处
                        truncate_pos = max_length
                        for punct in ['.', '!', '?', '\n']:
                            pos = content.rfind(punct, 0, max_length)
                            if pos > 0:
                                truncate_pos = max(truncate_pos, pos + 1)
                                break
                        content = content[:truncate_pos].rstrip() + "..."

                    formatted_results.append({
                        "content": content,
                        "source": meta.get("source", "未知来源"),
                        "distance": float(dist)
                    })

            # 3. 将结果存入缓存（24小时TTL）
            if formatted_results:
                self.cache_manager.set_cache(
                    query=query,
                    results=formatted_results,
                    top_k=top_k,
                    max_length=max_length,
                    ttl_hours=24
                )

            # 4. 打印统计信息
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"[RAG] 缓存未命中 | 耗时 {elapsed_ms}ms | 已缓存结果")

            return formatted_results

        except Exception as e:
            print(f"错误: 检索失败: {e}")
            print(traceback.format_exc())
            return []

    def is_available(self) -> bool:
        """检查RAG引擎是否可用"""
        return self.sentence_transformers_available


# 单例模式
_rag_instance = None

def get_rag_engine() -> RAGEngine:
    """获取RAG引擎实例（单例模式）"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGEngine()
    return _rag_instance


# 示例使用
if __name__ == "__main__":
    print("测试 RAGEngine...")

    rag = get_rag_engine()
    if not rag.is_available():
        print("RAG引擎不可用，请检查依赖")
        sys.exit(1)

    # 测试搜索
    test_queries = ["Q235材料强度", "M10螺栓规格", "公差配合IT7"]

    for query in test_queries:
        print(f"\n搜索: '{query}'")
        results = rag.search(query, top_k=2)

        if results:
            for i, result in enumerate(results, 1):
                print(f"结果 {i}:")
                print(f"  来源: {result['source']}")
                print(f"  相似度: {1 - result['distance']:.3f}")
                print(f"  内容: {result['content'][:100]}...")
        else:
            print("  未找到相关结果")