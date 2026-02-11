#!/usr/bin/env python3
"""
初始化 SQLite 数据库用于 CAE-CLI MCP 服务器
创建必要的表结构并导入现有数据
"""
import sqlite3
import json
import os
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "cae.db"
DATA_DIR = Path(__file__).parent / "data"

def init_database():
    """初始化数据库表结构"""
    print(f"初始化数据库: {DB_PATH}")

    # 确保 data 目录存在
    DATA_DIR.mkdir(exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 创建材料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        yield_strength REAL,
        elastic_modulus REAL,
        poisson_ratio REAL,
        density REAL,
        data JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. 创建知识库表（支持全文搜索）
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS knowledge
    USING fts5(
        id UNINDEXED,
        title,
        content,
        keywords,
        tokenize="porter"
    )
    """)

    # 3. 创建计算历史表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calc_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        input JSON NOT NULL,
        result JSON NOT NULL,
        analysis_type TEXT,
        metadata JSON
    )
    """)

    # 4. 创建材料查询索引
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_materials_category
    ON materials(category)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_materials_name
    ON materials(name)
    """)

    # 5. 创建计算历史索引
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_calc_history_timestamp
    ON calc_history(timestamp)
    """)

    # 提交更改
    conn.commit()

    # 检查表创建情况
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"已创建表: {[t[0] for t in tables]}")

    return conn, cursor

def import_materials_data(conn, cursor):
    """从 materials.json 导入材料数据"""
    materials_file = DATA_DIR / "materials.json"
    if not materials_file.exists():
        print(f"材料文件不存在: {materials_file}")
        return

    print(f"导入材料数据: {materials_file}")

    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_dict = json.load(f)

    imported_count = 0
    updated_count = 0

    for material_name, material in materials_dict.items():
        if not isinstance(material, dict):
            continue

        name = material.get('name', material_name)
        category = material.get('type', 'steel')  # 使用 type 字段作为类别

        # 提取关键属性
        yield_strength = material.get('yield_strength')
        elastic_modulus = material.get('elastic_modulus')
        poisson_ratio = material.get('poisson_ratio')
        density = material.get('density')

        # 检查材料是否已存在
        cursor.execute("SELECT id FROM materials WHERE name = ?", (name,))
        existing = cursor.fetchone()

        if existing:
            # 更新现有记录
            cursor.execute("""
            UPDATE materials
            SET category = ?, yield_strength = ?, elastic_modulus = ?,
                poisson_ratio = ?, density = ?, data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
            """, (category, yield_strength, elastic_modulus, poisson_ratio, density,
                  json.dumps(material, ensure_ascii=False), name))
            updated_count += 1
        else:
            # 插入新记录
            cursor.execute("""
            INSERT INTO materials
            (name, category, yield_strength, elastic_modulus, poisson_ratio, density, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, category, yield_strength, elastic_modulus, poisson_ratio, density,
                  json.dumps(material, ensure_ascii=False)))
            imported_count += 1

    conn.commit()
    print(f"材料数据导入完成: {imported_count} 条新增, {updated_count} 条更新")

    # 显示统计信息
    cursor.execute("SELECT COUNT(*) FROM materials")
    total = cursor.fetchone()[0]
    print(f"材料表总记录数: {total}")

    cursor.execute("SELECT category, COUNT(*) FROM materials GROUP BY category")
    categories = cursor.fetchall()
    print("按类别统计:")
    for category, count in categories:
        print(f"  {category}: {count}")

def add_sample_knowledge(conn, cursor):
    """添加示例知识库条目"""
    sample_entries = [
        {
            "title": "有限元分析基础",
            "content": "有限元分析（FEA）是一种数值方法，用于求解工程和数学物理问题。它将复杂系统分解为更小、更简单的部分，称为有限元。",
            "keywords": "FEA 有限元分析 数值方法 工程分析"
        },
        {
            "title": "材料力学性能指标",
            "content": "屈服强度：材料开始发生塑性变形的应力值。弹性模量：材料在弹性变形阶段的应力与应变之比。泊松比：材料横向应变与纵向应变的比值。",
            "keywords": "屈服强度 弹性模量 泊松比 材料性能"
        },
        {
            "title": "CAE分析流程",
            "content": "1. 几何建模 2. 网格划分 3. 材料定义 4. 边界条件设置 5. 求解计算 6. 后处理分析",
            "keywords": "CAE 分析流程 网格划分 求解"
        }
    ]

    for entry in sample_entries:
        cursor.execute("""
        INSERT INTO knowledge (title, content, keywords)
        VALUES (?, ?, ?)
        """, (entry['title'], entry['content'], entry['keywords']))

    conn.commit()
    print(f"添加了 {len(sample_entries)} 条示例知识库条目")

    cursor.execute("SELECT COUNT(*) FROM knowledge")
    total = cursor.fetchone()[0]
    print(f"知识库总条目数: {total}")

def main():
    """主函数"""
    print("=" * 60)
    print("CAE-CLI SQLite 数据库初始化")
    print("=" * 60)

    try:
        # 初始化数据库
        conn, cursor = init_database()

        # 导入材料数据
        import_materials_data(conn, cursor)

        # 添加示例知识库数据
        add_sample_knowledge(conn, cursor)

        # 显示数据库信息
        cursor.execute("PRAGMA database_list")
        databases = cursor.fetchall()
        for db in databases:
            print(f"数据库: {db[1]} (文件: {db[2]})")

        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        db_size = (page_count * page_size) / 1024  # KB
        print(f"数据库大小: {db_size:.2f} KB")

        print("\n[OK] 数据库初始化完成!")
        print(f"[DB] 数据库位置: {DB_PATH}")
        print(f"[TOOL] 表结构已创建，材料数据已导入")

    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'conn' in locals():
            conn.close()

    return 0

if __name__ == "__main__":
    exit(main())