# 🔥 Fanqie Hit Orchestrator (番茄小说爆款总控引擎 · 欲望满足向)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills Standard](https://img.shields.io/badge/Standard-AgentSkills.io-blue)](https://agentskills.io)
[![Multi-Agent Ready](https://img.shields.io/badge/Multi--Agent-Ready-green.svg)]()

> **Full-Lifecycle Fanqie Web Novel Hit Orchestrator Agent Skill (Desire-Driven Engine).**  
> 以 **`爆款 = 欲望靶点 × 压抑-兑现周期 × 章尾钩`** 为核心公式，按 **P0-P8 状态机** 全流程驱动番茄爽文创作：扫榜雷达与榜单监控 ➔ 欲望靶点选题 ➔ 爆款拆解与换皮微创新 ➔ 设定与伏笔账本 ➔ 黄金三章 ➔ 逐章连载 ➔ 去 AI 味与主编过签审计 ➔ 数据复盘。

---

## 🌟 核心特性 (Key Features)

1. **八大欲望靶点与毒点防御矩阵 (`01-desire-map.md`)**：
   - 精准锁定读者底层渴望（掌控/力量、尊严/打脸、财富/安全感、公平/复仇、被偏爱、重来/逃离、好奇/揭秘、归属/守护），内置番茄 9 大高频弃书毒点红线与五维立项评分卡。
2. **番茄黄金三章生死线 (`02-golden-three-chapters.md`)**：
   - 第 1 章 300 字抛冲突 + 立人设 + 亮钩子；第 2 章金手指生效 + 首次反击；第 3 章完成首个爽点闭环。
3. **单章四段引擎与六大断章钩 (`03-chapter-engine.md`)**：
   - `承钩 (0-15%) ➔ 加压 (15-60%) ➔ 兑现 (60-85%) ➔ 新钩 (85-100%)`，内置危机悬停、身份将揭、奖励预告、反派反扑、信息炸弹、选择困境 6 类章尾钩。
4. **金手指四要素与百章升级阶梯 (`04-cheat-and-progression.md`)**：
   - 强制锁定金手指“来源、规则、代价、上限”，实现主角能力、舞台地图、反派梯队三线同步升级。
5. **长篇唯一真相源防失忆账本 (`templates/state.md`)**：
   - 每次调用先读档、每写一章必更新，追踪数值面板、关键关系、伏笔借贷本与章节钩子交接。
6. **原生 PowerShell 自动化体检与榜单雷达 (`scripts/`)**：
   - 零外部依赖运行章节体检 (`text_lint.ps1`) 与榜单快照对比/标签红蓝海分析 (`rank_diff.ps1`)。

---

## 📂 仓库目录结构 (Architecture)

```text
fanqie-hit-orchestrator/
├── SKILL.md                             # 总控 Skill 核心入口与 P0-P8 状态机
├── README.md                            # 项目说明文档
├── LICENSE                              # MIT 开源协议
├── references/                          # 番茄爆款核心法则库
│   ├── 01-desire-map.md                 # 八大欲望靶点、毒点清单与选题评分卡
│   ├── 02-golden-three-chapters.md      # 黄金三章任务分配与自检表
│   ├── 03-chapter-engine.md             # 单章四段结构、爽点节奏与六种章尾钩
│   ├── 04-cheat-and-progression.md      # 金手指四要素与四卷成长阶梯
│   ├── 05-fanqie-compliance.md          # 网络文学合规硬红线与软风险替换方案
│   └── 06-trend-radar.md                # 扫榜雷达、CSV 快照规范与后台数据复盘
├── templates/                           # 标准化工程作业模板
│   ├── state.md                         # 项目唯一真相源（进度/数值/关系/伏笔账本）
│   ├── book-bible.md                    # 设定账本（世界观/金手指/人物卡/反派梯队）
│   ├── chapter-outline.md               # 分卷章纲与爽点节奏卡点表
│   ├── audit-report.md                  # 签约级八维审计打分报告模板
│   └── trend-report.md                  # 榜单趋势与黑马拆解报告模板
└── scripts/                             # 原生 PowerShell 自动化工具与词库
    ├── text_lint.ps1                    # 章节字数/段落/对话率/AI味/风险词/章尾钩体检
    ├── rank_diff.ps1                    # 榜单快照对比 (diff) 与标签热度统计 (tags)
    └── lexicons/
        ├── ai_cliche.txt                # AI 机械腔高频套话词库
        └── risk_words.txt               # 合规风险语境提示词库
```

---

## 🚀 快捷调用指令 (Quick Slash Commands)

| 指令 | 对应阶段 | 功能与产出 |
| :--- | :--- | :--- |
| `/radar [分类]` | P1 扫榜雷达 | 采集/分析榜单快照，输出红蓝海标签与黑马趋势报告 |
| `/monitor` | P1 爆款监控 | 与上一期快照执行 `rank_diff.ps1` 对比，追踪新上榜与飙升书目 |
| `/topic [方向]` | P2 欲望选题 | 锁定主副欲望靶点，输出 3 张五维打分选题卡 |
| `/dissect <书名/路径>` | P3 爆款拆解 | 拆解开篇钩、金手指闭环、反派梯队与爽点周期，输出换皮微创新方案 |
| `/bible` | P4 设定账本 | 生成 `bible.md`（含金手指四要素、反派梯队）与前 30 章细纲 |
| `/open` | P5 黄金三章 | 创作第 1-3 章并执行三章生死线自检 + `text_lint.ps1` |
| `/write [章号]` | P6 逐章连载 | 按单章四段结构创作正文，自动同步更新 `state.md` |
| `/lint <章节路径>` | P6/P7 体检 | 执行 `text_lint.ps1` 检测段落长度、对话占比、AI 味与章尾钩 |
| `/audit [范围]` | P7 润色审计 | 去 AI 味、主编 37 条铁律排查、合规红线复核，出具 S~C 级审计报告 |
| `/to-growth` | 跨总控协同 | 移交 `fanqie-growth-orchestrator` 进行“爽中有魂”升级 |

---

## 📦 安装与同步 (Installation & Sync)

直接克隆至项目的 `.agents/skills/` 目录即可与 GitHub 保持实时同步：

```bash
git clone https://github.com/cnproduct/fanqie-hit-orchestrator.git .agents/skills/fanqie-hit-orchestrator
```

> 建议与姊妹总控技能 [`fanqie-growth-orchestrator`](https://github.com/cnproduct/fanqie-growth-orchestrator) 同级安装于 `.agents/skills/` 下，以支持双总控协同调用。

---

## 📄 开源协议 (License)

本项目采用 [MIT License](LICENSE) 开源协议。
