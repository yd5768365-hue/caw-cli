"""
SQLite 数据库 MCP Server - 提供材料数据库查询、知识库搜索和计算历史管理
基于CAE-CLI项目需求定制
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from sw_helper.mcp.core import Tool, get_mcp_server


class SQLiteMCPServer:
    """
    SQLite数据库 MCP服务器
    为CAE-CLI提供材料数据库查询、知识库全文搜索和计算历史管理
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化SQLite MCP服务器

        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        self.server = get_mcp_server()
        if db_path is None:
            # 默认数据库路径
            self.db_path = Path.cwd() / "data" / "cae.db"
        else:
            self.db_path = Path(db_path)

        # 确保数据库文件存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._register_tools()

        print("[SQLite MCP] SQLite数据库MCP服务器已初始化")
        print(f"[SQLite MCP] 数据库路径: {self.db_path}")
        print(f"[SQLite MCP] 数据库存在: {self.db_path.exists()}")

    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 启用行工厂，返回字典-like对象
        return conn

    def _register_tools(self):
        """注册所有SQLite数据库工具"""

        # 1. 数据库信息
        self.server.register_tool(
            Tool(
                name="sqlite_db_info",
                description="获取SQLite数据库基本信息",
                input_schema={"type": "object", "properties": {}},
                handler=self._handle_db_info,
            )
        )

        # 2. 执行SQL查询
        self.server.register_tool(
            Tool(
                name="sqlite_execute_query",
                description="执行SQL查询语句",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "SQL查询语句"},
                        "parameters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "查询参数",
                            "default": [],
                        },
                    },
                    "required": ["sql"],
                },
                handler=self._handle_execute_query,
            )
        )

        # 3. 材料查询
        self.server.register_tool(
            Tool(
                name="sqlite_query_materials",
                description="查询材料数据",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "材料名称（支持模糊查询）"},
                        "category": {"type": "string", "description": "材料类别"},
                        "min_yield_strength": {"type": "number", "description": "最小屈服强度 (Pa)"},
                        "max_yield_strength": {"type": "number", "description": "最大屈服强度 (Pa)"},
                        "limit": {"type": "integer", "description": "返回结果数量限制", "default": 50},
                    },
                },
                handler=self._handle_query_materials,
            )
        )

        # 4. 知识库全文搜索
        self.server.register_tool(
            Tool(
                name="sqlite_search_knowledge",
                description="在知识库中全文搜索",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "limit": {"type": "integer", "description": "返回结果数量限制", "default": 20},
                    },
                    "required": ["query"],
                },
                handler=self._handle_search_knowledge,
            )
        )

        # 5. 添加计算历史
        self.server.register_tool(
            Tool(
                name="sqlite_add_calc_history",
                description="添加计算历史记录",
                input_schema={
                    "type": "object",
                    "properties": {
                        "input": {"type": "object", "description": "计算输入参数"},
                        "result": {"type": "object", "description": "计算结果"},
                        "analysis_type": {"type": "string", "description": "分析类型（如static, modal, thermal等）"},
                        "metadata": {"type": "object", "description": "额外元数据"},
                    },
                    "required": ["input", "result"],
                },
                handler=self._handle_add_calc_history,
            )
        )

        # 6. 查询计算历史
        self.server.register_tool(
            Tool(
                name="sqlite_query_calc_history",
                description="查询计算历史记录",
                input_schema={
                    "type": "object",
                    "properties": {
                        "analysis_type": {"type": "string", "description": "分析类型"},
                        "start_date": {"type": "string", "description": "开始日期（YYYY-MM-DD格式）"},
                        "end_date": {"type": "string", "description": "结束日期（YYYY-MM-DD格式）"},
                        "limit": {"type": "integer", "description": "返回结果数量限制", "default": 50},
                    },
                },
                handler=self._handle_query_calc_history,
            )
        )

        # 7. 添加知识库条目
        self.server.register_tool(
            Tool(
                name="sqlite_add_knowledge",
                description="添加知识库条目",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "条目标题"},
                        "content": {"type": "string", "description": "条目内容"},
                        "keywords": {"type": "string", "description": "关键词（空格分隔）"},
                    },
                    "required": ["title", "content"],
                },
                handler=self._handle_add_knowledge,
            )
        )

        # 8. 数据库备份
        self.server.register_tool(
            Tool(
                name="sqlite_backup_db",
                description="备份数据库",
                input_schema={
                    "type": "object",
                    "properties": {"backup_path": {"type": "string", "description": "备份文件路径（可选）"}},
                },
                handler=self._handle_backup_db,
            )
        )

        print(f"[SQLite MCP] 已注册 {len(self.server.tools)} 个数据库工具")

    # ===== 工具处理器 =====

    def _handle_db_info(self) -> Dict[str, Any]:
        """处理数据库信息请求"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取表信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # 获取数据库大小
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

            # 获取各表记录数
            table_counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                except Exception:
                    table_counts[table] = 0

            conn.close()

            return {
                "success": True,
                "db_path": str(self.db_path),
                "db_size": db_size,
                "tables": tables,
                "table_counts": table_counts,
                "exists": self.db_path.exists(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_execute_query(self, sql: str, parameters: Optional[List[str]] = None) -> Dict[str, Any]:
        """处理SQL查询执行"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            params = parameters or []
            cursor.execute(sql, params)

            # 判断查询类型
            sql_upper = sql.strip().upper()
            if sql_upper.startswith("SELECT"):
                # 查询语句，返回结果
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                result = [dict(zip(columns, row)) for row in rows]

                return {"success": True, "type": "query", "row_count": len(result), "columns": columns, "data": result}
            else:
                # DML语句（INSERT, UPDATE, DELETE等）
                conn.commit()
                affected_rows = cursor.rowcount

                return {"success": True, "type": "dml", "affected_rows": affected_rows, "lastrowid": cursor.lastrowid}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_query_materials(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        min_yield_strength: Optional[float] = None,
        max_yield_strength: Optional[float] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """处理材料查询请求"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 构建查询条件
            conditions = []
            params = []

            if name:
                conditions.append("(name LIKE ? OR data LIKE ?)")
                params.extend([f"%{name}%", f"%{name}%"])

            if category:
                conditions.append("category = ?")
                params.append(category)

            if min_yield_strength is not None:
                conditions.append("yield_strength >= ?")
                params.append(min_yield_strength)

            if max_yield_strength is not None:
                conditions.append("yield_strength <= ?")
                params.append(max_yield_strength)

            # 构建SQL
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            sql = f"""
            SELECT id, name, category, yield_strength, elastic_modulus,
                   poisson_ratio, density, data, created_at, updated_at
            FROM materials
            WHERE {where_clause}
            ORDER BY name
            LIMIT ?
            """
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # 转换为字典列表
            materials = []
            for row in rows:
                material = dict(row)
                # 解析JSON数据
                if material.get("data"):
                    try:
                        material["data"] = json.loads(material["data"])
                    except json.JSONDecodeError:
                        pass
                materials.append(material)

            conn.close()

            return {
                "success": True,
                "count": len(materials),
                "materials": materials,
                "query": {
                    "name": name,
                    "category": category,
                    "min_yield_strength": min_yield_strength,
                    "max_yield_strength": max_yield_strength,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_search_knowledge(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """处理知识库全文搜索请求"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            sql = """
            SELECT id, title, content, keywords,
                   snippet(knowledge, 2, '<b>', '</b>', '...', 30) as snippet,
                   rank
            FROM knowledge
            WHERE knowledge MATCH ?
            ORDER BY rank
            LIMIT ?
            """

            cursor.execute(sql, (query, limit))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append(dict(row))

            conn.close()

            return {"success": True, "query": query, "count": len(results), "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_add_calc_history(
        self,
        input: Dict[str, Any],
        result: Dict[str, Any],
        analysis_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """处理添加计算历史请求"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            sql = """
            INSERT INTO calc_history (input, result, analysis_type, metadata)
            VALUES (?, ?, ?, ?)
            """

            cursor.execute(
                sql,
                (
                    json.dumps(input, ensure_ascii=False),
                    json.dumps(result, ensure_ascii=False),
                    analysis_type,
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )

            conn.commit()
            history_id = cursor.lastrowid

            conn.close()

            return {"success": True, "history_id": history_id, "timestamp": "now", "analysis_type": analysis_type}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_query_calc_history(
        self,
        analysis_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """处理查询计算历史请求"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            conditions = []
            params = []

            if analysis_type:
                conditions.append("analysis_type = ?")
                params.append(analysis_type)

            if start_date:
                conditions.append("date(timestamp) >= ?")
                params.append(start_date)

            if end_date:
                conditions.append("date(timestamp) <= ?")
                params.append(end_date)

            where_clause = " AND ".join(conditions) if conditions else "1=1"
            sql = f"""
            SELECT id, timestamp, input, result, analysis_type, metadata
            FROM calc_history
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
            """
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # 转换结果
            history_items = []
            for row in rows:
                item = dict(row)
                # 解析JSON字段
                for field in ["input", "result", "metadata"]:
                    if item.get(field):
                        try:
                            item[field] = json.loads(item[field])
                        except json.JSONDecodeError:
                            pass
                history_items.append(item)

            conn.close()

            return {
                "success": True,
                "count": len(history_items),
                "history": history_items,
                "query": {"analysis_type": analysis_type, "start_date": start_date, "end_date": end_date},
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_add_knowledge(self, title: str, content: str, keywords: Optional[str] = None) -> Dict[str, Any]:
        """处理添加知识库条目请求"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            sql = """
            INSERT INTO knowledge (title, content, keywords)
            VALUES (?, ?, ?)
            """

            cursor.execute(sql, (title, content, keywords or ""))
            conn.commit()
            knowledge_id = cursor.lastrowid

            conn.close()

            return {"success": True, "knowledge_id": knowledge_id, "title": title, "keywords": keywords}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_backup_db(self, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """处理数据库备份请求"""
        try:
            if not self.db_path.exists():
                return {"success": False, "error": "源数据库文件不存在"}

            import datetime
            import shutil

            if backup_path is None:
                # 生成默认备份路径
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = str(self.db_path.parent / f"cae_backup_{timestamp}.db")

            backup_path_obj = Path(backup_path)
            backup_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # 复制数据库文件
            shutil.copy2(self.db_path, backup_path_obj)

            return {
                "success": True,
                "backup_path": str(backup_path_obj),
                "original_path": str(self.db_path),
                "backup_size": backup_path_obj.stat().st_size,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局SQLite MCP Server实例
_sqlite_mcp_server: Optional[SQLiteMCPServer] = None


def get_sqlite_mcp_server(db_path: Optional[str] = None) -> SQLiteMCPServer:
    """获取全局SQLite MCP服务器"""
    global _sqlite_mcp_server
    if _sqlite_mcp_server is None:
        _sqlite_mcp_server = SQLiteMCPServer(db_path)
    return _sqlite_mcp_server
