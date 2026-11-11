# 🖋️ xiaoshuo-jia (长篇小说全流程创作与交付专家)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

> **端到端的长篇网文小说工业级生产线。**  
> 覆盖从世界观/大纲规划、分章生成（2200-2800字/章、五幕结构、钩子轮换）、质量评估、人物补强、去AI味手术级精修、到平台发布准备的全链路。

---

## 核心特性

1. **阶段① 规划体系 (`references/planning.md`)**：
   - 五幕结构全卷切割、五型钩子（信息差/危机逼近/关系转折/身份揭秘/收束留白）轮换表。
2. **阶段② 严格字数与钩子生成**：
   - 2200-2800 字/章网文黄金体量纪律，带伏笔标记与章尾高能钩子。
3. **阶段③ 质量评估 (`references/evaluation.md`)**：
   - 字数纪律合规、钩子轮换检测器（`hook_rotation_check.py`）、字数检查（`wordcount_check.py`）。
4. **阶段④ 手术级去 AI 味精修 (`references/deai.md`)**：
   - 拒绝大段重写破坏字数，专注面部微表情、机械连接词、空泛议论的局部精准手术。
5. **阶段⑤ 平台发布准备 (`references/publishing.md`)**：
   - 元数据剥离工具（`strip_metadata.py`）、平台简介与上架信息单输出。

---

## 目录结构

```text
xiaoshuo-jia/
├── SKILL.md                          # 技能入口与全阶段工业规范
├── README.md                         # 模块说明文档
├── LICENSE                           # MIT 开源协议
├── _meta.json                        # 技能元数据
├── references/                       # 核心操作规范
│   ├── deai.md                       # 手术级去 AI 味润色指南
│   ├── evaluation.md                 # 质量评估与验收标尺
│   ├── planning.md                   # 五幕大纲与钩子轮换设计
│   └── publishing.md                 # 平台元数据清洗与发布指南
├── templates/                        # 标准模板
│   ├── chapter-template.md           # 章节结构模板
│   └── outline-template.md           # 大纲与情绪曲线模板
└── scripts/                          # 工具脚本
    ├── hook_rotation_check.py        # 钩子轮换与相邻冲突检测器
    ├── strip_metadata.py             # 章节元数据剥离脚本
    └── wordcount_check.py            # 纯字数合规检查器
```

---

## 许可证

MIT License
