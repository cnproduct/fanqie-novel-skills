# 🌱 Fanqie Growth Orchestrator (番茄小说成长向总控引擎 · 真我与良知的精神食粮)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills Standard](https://img.shields.io/badge/Standard-AgentSkills.io-blue)](https://agentskills.io)
[![Multi-Agent Ready](https://img.shields.io/badge/Multi--Agent-Ready-green.svg)]()

> **Full-Lifecycle Fanqie Web Novel Growth & Conscience Orchestrator Agent Skill.**  
> 保留番茄网文的强追读力（黄金三章、章尾钩、短段落白描），将兑现物从单纯的“欲望宣泄”升级为“**内在觉醒与良知回响**”。  
> 核心公式：**`成长 = 真实困境 × 错误信念被代价击碎 × 主动选择 × 良知回响`**（以钩引心，以爽载道）。

---

## 🌟 核心特性 (Key Features)

1. **欲望 ➔ 深层需要转化地图 (`01-inner-need-map.md`)**：
   - 读者以表层欲望（变强、打脸、暴富、复仇、被偏爱、重来）入场，在故事推进中照见深层精神需要（内在安定、自我价值、承担与和解、正义而非私怨）。
2. **四阶成长弧：迷 ➔ 觉 ➔ 行 ➔ 合 (`02-growth-arc.md`)**：
   - 融合王阳明“事上磨练、知行合一”与经典剧作人物弧光：错误信念带来初期爽点（迷）➔ 真实代价击碎旧信念（觉）➔ 尝试新选择与高压倒退（行）➔ 终局镜像选择（合）。
3. **以钩引心：爽点 ➔ 觉点升级矩阵 (`03-hook-with-meaning.md`)**：
   - 保持 60%-70% 经典爽点维持追读，将 30%-40% 关键节点升级为“觉点”，并拓展道德两难钩、真相照见钩、关系裂缝钩、自我怀疑钩、代价降临钩。
4. **反说教九病手术刀 (`04-anti-preachiness.md` & `preachy.txt`)**：
   - 严禁旁白总结道理、导师长篇宣讲、章尾感悟升华与无代价顿悟；一切主题只靠人物在两难中的具体行动证明。
5. **追读力 × 精神价值双轴审计 (`05-conscience-audit.md`)**：
   - 同时考核商业追读力与良知八维标尺（真实性、代价、主动选择、反命题强度、人物尊严、不说教、余味、正向牵引），杜绝鸡汤、成功学与道德优越感。

---

## 📂 仓库目录结构 (Architecture)

```text
fanqie-growth-orchestrator/
├── SKILL.md                             # 总控 Skill 核心入口与 G0-G8 状态机
├── README.md                            # 项目说明文档
├── LICENSE                              # MIT 开源协议
├── references/                          # 成长与良知核心方法库
│   ├── 01-inner-need-map.md             # 八大欲望→深层需要转化表与心灵痛点雷达
│   ├── 02-growth-arc.md                 # 迷→觉→行→合四阶成长弧与代价/镜像设计
│   ├── 03-hook-with-meaning.md          # 爽点→觉点转化矩阵与五类成长向章尾钩
│   ├── 04-anti-preachiness.md           # 说教九种病症诊断与“只呈现不评判”改写范例
│   └── 05-conscience-audit.md           # 良知八维标尺、精神红线与读者回响复盘
├── templates/                           # 标准化工程作业模板
│   ├── soul-bible.md                    # 灵魂账本（创伤/错误信念/黑白镜像/对手正当逻辑）
│   ├── growth-outline.md                # 外部爽点线 × 内部觉点线双线对位章纲
│   └── dual-audit-report.md             # 追读力 × 精神价值双轴审计报告模板
└── scripts/
    └── lexicons/
        └── preachy.txt                  # 说教腔、鸡汤腔、主题词直出检测词库
```

---

## 🚀 快捷调用指令 (Quick Slash Commands)

| 指令 | 对应阶段 | 功能与产出 |
| :--- | :--- | :--- |
| `/pulse [人群/题材]` | G1 心灵雷达 | 扫描榜单趋势 + 读者心灵痛点，定位集体情绪与错误信念 |
| `/theme [想法]` | G2 立意反命题 | 构建“入口欲望 ➔ 深层需要 ➔ 主题命题 ➔ 最强反命题”立意卡 |
| `/soul` | G3 灵魂账本 | 生成 `soul-bible.md`（主角创伤、错误信念、黑白镜人物、对手自洽逻辑） |
| `/arc` | G4 成长弧大纲 | 输出 `growth-outline.md`，实现外部爽点线与内部觉点线双线对位 |
| `/open` | G5 黄金三章 | 以危机/欲望开局并暗埋“内在裂缝”，零说教通过黄金三章自检 |
| `/write [章号]` | G6 逐章连载 | 按“承钩 ➔ 事上磨练 ➔ 选择时刻 ➔ 余味+新钩”创作正文并更新 `state.md` |
| `/deepen <章节路径>` | 爽文加魂 | 在不削弱爽感的前提下，将既有爽点升级为有余味的觉点 |
| `/depreach <章节路径>` | 去说教改写 | 扫描并清除旁白总结、导师说教与口号式台词，改为动作与细节呈现 |
| `/audit [范围]` | G7 双重审计 | 执行追读力轴 + 精神价值轴双重审计及 `preachy.txt` 扫描 |
| `/echo` | G8 回响复盘 | 分析读者共鸣、反思、争论与弃书反馈，动态修正后续成长弧 |

---

## 📦 安装与同步 (Installation & Sync)

直接克隆至项目的 `.agents/skills/` 目录即可与 GitHub 保持实时同步：

```bash
git clone https://github.com/cnproduct/fanqie-growth-orchestrator.git .agents/skills/fanqie-growth-orchestrator
```

> 建议与 [`fanqie-hit-orchestrator`](https://github.com/cnproduct/fanqie-hit-orchestrator) 同级安装于 `.agents/skills/` 下，以复用榜单快照对比与 `text_lint.ps1` 文本体检引擎。

---

## 📄 开源协议 (License)

本项目采用 [MIT License](LICENSE) 开源协议。
