# 🩺 novel-style-doctor (网文文风诊断与双轨评分参谋)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

> **网文文风诊断与投稿双轨评分专家技能。**  
> 内置 `style_scan.py` 算法扫描器 + 番茄平台专属双轨评分模型（文学六维 + 平台六维），用客观数据替代主观猜测，回答“我的文字像不像机器写、能不能签约、值不值得投”。

---

## 核心特性

1. **客观检测半区 (`scripts/style_scan.py`)**：
   - 困惑度代理（高频虚词、逻辑连接词、bigram 重复率）
   - 爆发度特征（句长 CV、段长 CV、章字数波动）
   - 统计指纹（黑名单词、高频副词、套路标点）
   - 情感扁平度与低质水文检测（对话占比、流水账连接词、具体性密度）
   - 综合输出 0~1 的 AIGC 特征值与逐章风险报告
2. **专业双轨评分半区 (`references/tomato-evaluator.md`)**：
   - **文学六维**：情节、人物、文笔、世界观、情感、创新（满分 100 分）
   - **平台六维**：合规安全、签约竞争力、完读率设计、文风健康度、商业包装、体量形态（满分 100 分）
   - 综合输出投资回报预测与行动清单

---

## 目录结构

```text
novel-style-doctor/
├── SKILL.md                          # 技能入口与工作流定义
├── README.md                         # 模块说明文档
├── LICENSE                           # MIT 开源协议
├── _meta.json                        # 技能元数据
├── references/                       # 评分准则与方法手册
│   ├── scoring-rubric.md             # 详细评分量表
│   ├── style-principles.md          # 诊断算法原理
│   └── tomato-evaluator.md          # 番茄双轨评审细则
└── scripts/
    └── style_scan.py                 # 本地独立 AIGC 与文风质量扫描器
```

---

## 快速使用

```bash
python scripts/style_scan.py <小说文件路径> [--json 输出结果.json]
```

---

## 许可证

MIT License
