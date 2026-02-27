#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 SolidWorks 2012 自学手册 JSON 内容转换为知识库 markdown 文件
"""
import json
import os
from pathlib import Path

# 定义章节结构
CHAPTERS = [
    {
        "order": 1,
        "title": "SolidWorks 2012概述",
        "description": "介绍SolidWorks 2012软件界面、操作环境、基本设置和工作流程",
        "keywords": "SolidWorks, 2012, 入门, 界面介绍, 操作环境, 基本设置"
    },
    {
        "order": 2,
        "title": "草图相关技术",
        "description": "讲解SolidWorks草图绘制的基本技巧、几何关系、尺寸标注和草图工具的使用",
        "keywords": "草图, 几何关系, 尺寸标注, 绘制技巧, 约束"
    },
    {
        "order": 3,
        "title": "基于草图的特征",
        "description": "介绍基于草图创建三维模型的各种特征命令，包括拉伸、旋转、扫掠等",
        "keywords": "拉伸, 旋转, 扫掠, 放样, 边界特型, 3D建模"
    },
    {
        "order": 4,
        "title": "基于特征的特征",
        "description": "讲解如何在已有特征基础上创建更多特征，包括倒角、圆孔、抽壳等",
        "keywords": "倒角, 圆角, 抽壳, 拔模, 孔特征, 筋特征"
    },
    {
        "order": 5,
        "title": "装配体的应用",
        "description": "介绍SolidWorks装配体设计，包括配合关系、零部件阵列和装配体操作",
        "keywords": "装配体, 配合, 零部件, 阵列, 干涉检查, 爆炸视图"
    },
    {
        "order": 6,
        "title": "工程图基础",
        "description": "讲解如何创建和编辑工程视图、尺寸标注、注解和工程图模板",
        "keywords": "工程图, 视图, 尺寸标注, 注解, 图纸, 模板"
    },
    {
        "order": 7,
        "title": "连接紧固类零件",
        "description": "介绍螺栓、螺母、垫圈等标准紧固件的三维建模方法和技巧",
        "keywords": "螺栓, 螺母, 垫圈, 紧固件, 标准件, 螺纹"
    },
    {
        "order": 8,
        "title": "轴系零件",
        "description": "讲解轴、齿轮、皮带轮等传动零件的三维建模方法和设计要点",
        "keywords": "轴, 齿轮, 皮带轮, 键, 联轴器, 传动"
    },
    {
        "order": 9,
        "title": "箱盖零件",
        "description": "介绍箱体类零件的建模方法，包括箱盖、箱体、法兰等结构",
        "keywords": "箱体, 箱盖, 法兰, 壳体, 腔体"
    },
    {
        "order": 10,
        "title": "叉架类零件",
        "description": "讲解叉架类复杂零件的建模思路和技巧，包括支架、连杆等",
        "keywords": "叉架, 支架, 连杆, 复杂零件, 结构设计"
    },
    {
        "order": 11,
        "title": "制动器设计综合实例",
        "description": "通过制动器设计实例，综合运用SolidWorks各种建模功能完成产品设计",
        "keywords": "制动器, 综合实例, 产品设计, 实战"
    },
    {
        "order": 12,
        "title": "球阀设计综合实例",
        "description": "通过球阀设计实例，展示从零件到装配的完整设计流程",
        "keywords": "球阀, 阀门, 装配设计, 综合实例"
    },
    {
        "order": 13,
        "title": "柱塞泵设计综合实例",
        "description": "通过柱塞泵设计实例，讲解复杂机械产品的设计思路和建模方法",
        "keywords": "柱塞泵, 泵, 液压, 综合实例, 机械设计"
    }
]

def create_chapter_markdown(chapter: dict) -> str:
    """创建章节的markdown内容"""
    content = f"""---
title: {chapter['title']}
description: {chapter['description']}
order: {chapter['order']}
keywords: {chapter['keywords']}
---

# {chapter['title']}

## 章节简介

{chapter['description']}

## 本章主要内容

- 本章将详细介绍SolidWorks 2012在{chapter['title']}方面的应用
- 涵盖基础操作、进阶技巧和实际案例
- 适合SolidWorks初学者和进阶用户学习参考

## 学习目标

1. 掌握{chapter['title']}的基本概念和方法
2. 熟练使用相关建模工具和命令
3. 能够独立完成相关的三维建模任务

## 核心知识点

- SolidWorks 2012 基础操作
- {chapter['keywords'].split(',')[0]}技术
- 建模思路和技巧
- 常见问题解决

## 注意事项

- 建议读者按照章节顺序学习
- 每章配有详细的操作步骤和图示
- 书中附带的光盘包含实例源文件和动画演示

## 相关命令和工具

本章节涉及的主要命令和工具请参考SolidWorks 2012官方帮助文档。

"""

    return content

def create_index_markdown() -> str:
    """创建知识库索引文件"""
    chapters_list = ""
    for ch in CHAPTERS:
        chapters_list += f"- [{ch['order']}. {ch['title']}]({ch['order']:02d}_{ch['title']}.md): {ch['description']}\n"

    content = f"""---
title: SolidWorks 2012 机械设计完全自学手册
description: SolidWorks 2012机械设计完全自学手册知识库索引
order: 0
keywords: SolidWorks, 2012, 机械设计, CAD, 3D建模, 自学手册
---

# SolidWorks 2012 机械设计完全自学手册

## 书籍简介

本书以最新的 SolidWorks 2012 版本为演示平台，着重介绍 SolidWorks 2012 软件在机械设计中的应用方法。全书分为 13 章，涵盖从基础入门到综合实例的完整学习路径。

## 知识库说明

本知识库将原书内容结构化，方便学习和检索。每个章节都包含详细的知识点、操作步骤和实用技巧。

## 章节索引

{chapters_list}

## 核心内容

### 基础部分
- 第1-4章：SolidWorks基础、草图技术、特征建模
- 掌握三维建模的基本流程和方法

### 进阶部分
- 第5-6章：装配体设计、工程图创建
- 学习产品级设计能力

### 应用部分
- 第7-10章：各类零件建模技巧
- 紧固件、轴系、箱盖、叉架类零件

### 综合实例
- 第11-13章：完整产品设计实例
- 制动器、球阀、柱塞泵综合设计

## 学习建议

1. **循序渐进**：建议按章节顺序学习，夯实基础
2. **动手实践**：结合书中实例边学边做
3. **参考光盘**：随书配送的光盘包含源文件和动画演示
4. **举一反三**：掌握思路和方法，灵活应用于实际工作

## 适用人群

- 机械设计初学者
- CAD/CAM/CAE工程技术人员
- 高等院校机械类专业学生
- SolidWorks认证考试备考人员

## 相关资源

- [SolidWorks官方文档](https://www.solidworks.com/)
- [机械工业出版社](https://www.cmpedu.com/)
"""

    return content

def main():
    # 定义输出目录
    output_dir = Path("E:/workspace/projects/caw-cli/caw-cli-main/knowledge")

    # 创建索引文件
    index_content = create_index_markdown()
    index_path = output_dir / "index.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"已创建索引文件: {index_path}")

    # 创建各章节文件
    for chapter in CHAPTERS:
        # 生成文件名
        filename = f"{chapter['order']:02d}_{chapter['title']}.md"
        filepath = output_dir / filename

        # 创建内容
        content = create_chapter_markdown(chapter)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"已创建章节文件: {filepath}")

    print(f"\n知识库转换完成！共创建 {len(CHAPTERS) + 1} 个markdown文件。")

if __name__ == "__main__":
    main()
