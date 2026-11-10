---
name: fanqie-hit-orchestrator
description: >-
  番茄小说爆款总控引擎（欲望满足向）。以"欲望靶点 × 压抑-兑现周期 × 章尾钩"为核心，
  按 P0-P8 状态机推进：扫榜雷达与榜单监控 → 欲望靶点选题 → 爆款拆解与换皮微创新 → 设定与伏笔账本 →
  黄金三章 → 逐章连载 → 去AI味与过签审计 → 数据复盘。各阶段按需调用本地子技能
  （short-drama、screenwriter-skill、screenwriting-skills、zenstory-drama-skills、drama-trend-rewriter）。
  当用户要写番茄爽文/爆款网文、扫榜选题、监控榜单变化、拆解爆款、设计金手指与黄金三章、续写章节、
  去AI味或做签约前审核时使用。若用户要的是成长/治愈/精神价值向作品，转交 fanqie-growth-orchestrator。
---

# 番茄小说爆款总控引擎（Fanqie Hit Orchestrator）

> **定位**：精准命中读者欲望，并在 100 万字里持续、有节奏地兑现。
> **核心公式**：`爆款 = 欲望靶点（写给谁的什么渴望） × 压抑-兑现周期（爽感节奏） × 章尾钩（追读力）`

本技能是**总控**：只负责流程推进、记忆管理、子技能调度和质量闸口。专业知识按阶段**按需加载**，不要一次性读完所有参考文件。

---

## 一、总控五原则

1. **先定靶点再写字**：任何选题、章节都必须先回答"这一段满足读者哪种欲望"（见 [01-desire-map.md](references/01-desire-map.md)）。
2. **账本即记忆**：长篇不靠上下文记忆，靠项目文件。每次被调用，**先读 `state.md`**，每写完一章**必须更新**。
3. **每章一爽一钩**：每章至少一个可感知的兑现点（小爽）+ 章尾一个钩子；压抑不连续超过 2 章。
4. **按需调度**：只读当前阶段需要的子技能文件和章节，避免提示词互相污染。
5. **底线不可越**：合规红线（[05-fanqie-compliance.md](references/05-fanqie-compliance.md)）优先于一切爽感。

---

## 二、项目目录约定

每本书在工作区建立独立目录（首次启动时由 P0 创建）：

```
novels/<书名>/
├── state.md              # 唯一真相源：当前阶段、最新章节、战力/资产、未回收伏笔（模板：templates/state.md）
├── 00-radar/             # 榜单快照 CSV、趋势报告
├── 01-bible/             # bible.md（设定+人物+金手指）
├── 02-outline/           # 卷纲、章纲
├── 03-chapters/          # 第001章.md ...
└── 04-audit/             # 体检报告、审计报告
```

---

## 三、阶段状态机（P0-P8）

| 阶段 | 触发 | 核心动作 | 调度 | 产出 | 闸口（不过不进下一阶段） |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P0 读档/建档** | 每次调用 | 读取或创建 `state.md`，判断当前阶段 | [templates/state.md](templates/state.md) | state.md | 阶段明确 |
| **P1 扫榜雷达** | `/radar` "现在什么火" | 收集榜单快照 → 对比 → 标签热度 → 蓝海/红海判断 | [06-trend-radar.md](references/06-trend-radar.md)、`scripts/rank_diff.ps1` | `00-radar/趋势报告.md`（[模板](templates/trend-report.md)） | 有数据来源与日期 |
| **P2 欲望选题** | `/topic` | 锁定欲望靶点 → 出 3 张选题卡 → 五维打分 | [01-desire-map.md](references/01-desire-map.md)、`../short-drama/references/genre-guide.md`、`sw-premise-theme`（logline 测试） | 选题卡 ×3 | **用户选定一个** |
| **P3 爆款拆解** | `/dissect <书>` | 拆骨架：开篇钩、金手指闭环、反派梯队、爽点周期 → 换皮/反套路 | `zenstory .../short-drama-novel-analyze`、`../drama-trend-rewriter`（模式 A 换皮 / B 反套路） | 拆解卡 + 差异化清单 | 符合"借骨不借肉" |
| **P4 设定账本** | `/bible` | 世界观、人物、金手指四要素、反派梯队、前 30 章章纲 | [04-cheat-and-progression.md](references/04-cheat-and-progression.md)、`../short-drama/references/villain-design.md`、`sw-character-conflict`、`sw-series-engine-bible` | `bible.md`（[模板](templates/book-bible.md)）、章纲（[模板](templates/chapter-outline.md)） | 金手指**有代价、有上限、有成长曲线** |
| **P5 黄金三章** | `/open` | 写第 1-3 章 | [02-golden-three-chapters.md](references/02-golden-three-chapters.md)、`../short-drama/references/opening-rules.md`、`hook-design.md` | 第 001-003 章 | 通过三章自检表 + `text_lint.ps1` |
| **P6 逐章连载** | `/write [N]` "继续写" | 按章纲写单章 → 更新 state.md | [03-chapter-engine.md](references/03-chapter-engine.md)、`../short-drama/references/satisfaction-matrix.md`、`rhythm-curve.md` | 第 N 章 | 一爽一钩、字数达标 |
| **P7 润色审计** | `/audit` 或每 10 章自动 | 文本体检 → 去 AI 味 → 主编铁律 → 合规 | `scripts/text_lint.ps1`、`zenstory .../anti-template-repair.md`、`../script-super-orchestrator/references/04-iron-rules-and-anti-ai.md`、`../screenwriter-skill/references/iron_rules.md`、[05-fanqie-compliance.md](references/05-fanqie-compliance.md) | `04-audit/审计报告.md`（[模板](templates/audit-report.md)） | 综合评级 ≥ A，无合规红灯 |
| **P8 数据复盘**（可选） | `/review-data` | 用户提供作者后台数据（读完率、追读、加书架、评论） → 定位掉点章节 → 调整后续章纲 | [06-trend-radar.md](references/06-trend-radar.md) 第四节 | 复盘结论 + 章纲修订 | — |

> 用户可以从任意阶段切入（例如直接拿已有大纲要求续写）。此时 P0 先补齐 `state.md` 的必填项，再进入对应阶段。

---

## 四、快捷指令

| 指令 | 作用 |
| :--- | :--- |
| `/radar [分类]` | 扫榜 + 趋势报告（P1） |
| `/monitor` | 与上一份快照做对比，输出变化（P1，可配合 `/schedule` 做周期提醒） |
| `/topic [方向]` | 欲望靶点选题，出 3 张选题卡（P2） |
| `/dissect <书名/文本路径>` | 爆款拆解 + 换皮方案（P3） |
| `/bible` | 生成/更新设定账本（P4） |
| `/open` | 写黄金三章（P5） |
| `/write [章号]` | 写下一章或指定章（P6） |
| `/lint <章节路径>` | 跑文本体检脚本 |
| `/audit [章节范围]` | 主编级审计（P7） |
| `/status` | 输出 state.md 摘要：进度、战力、未回收伏笔 |
| `/to-growth` | 把当前项目交给 `fanqie-growth-orchestrator` 做"爽中有魂"加固 |

---

## 五、子技能调度表（路径相对本技能目录）

| 子技能 / 文件 | 何时加载 | 只读哪部分 |
| :--- | :--- | :--- |
| `../short-drama/references/genre-guide.md` | P2 | 目标题材条目 |
| `../short-drama/references/opening-rules.md`、`hook-design.md` | P5、P6 | 开篇法则、钩子类型 |
| `../short-drama/references/satisfaction-matrix.md`、`rhythm-curve.md` | P4 卷纲、P6 | 爽感矩阵、节奏曲线 |
| `../short-drama/references/villain-design.md` | P4 | 反派分层 |
| `../short-drama/references/compliance-checklist.md` | P7 | 全文 |
| `../screenwriter-skill/references/iron_rules.md`、`templates/review_template.md` | P7 | 铁律逐条对照 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-premise-theme/` | P2 | logline 测试 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-character-conflict/` | P4 | 人物冲突设计 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-series-engine-bible/` | P4 | 长线连载"故事引擎" |
| `../zenstory-drama-skills/skills/short-drama-novel-analyze/` | P3 | 章节索引与拆解流程 |
| `../zenstory-drama-skills/skills/short-drama-review/references/anti-template-repair.md` | P7 | 反套路修复 |
| `../script-super-orchestrator/references/04-iron-rules-and-anti-ai.md` | P7 | 去 AI 味部分 |
| `../drama-trend-rewriter/` | P3；网文→短剧改编 | 模式 A/B；改编时全文 |
| `../fanqie-growth-orchestrator/` | 用户要求立意/人物深度 | 由该总控接管 |

---

## 六、工具脚本（PowerShell 5.1+，无需 Python）

```powershell
# 章节体检：字数、段落、对话占比、AI味/风险词命中、章尾钩子检测
powershell -ExecutionPolicy Bypass -File scripts/text_lint.ps1 -Path "novels/<书名>/03-chapters/第001章.md" -Out "novels/<书名>/04-audit/lint-001.md"
# 可叠加自定义词库（例如成长向的说教词库）
powershell -ExecutionPolicy Bypass -File scripts/text_lint.ps1 -Path <章节> -Lexicon "../fanqie-growth-orchestrator/scripts/lexicons/preachy.txt"

# 榜单快照对比 / 标签热度
powershell -ExecutionPolicy Bypass -File scripts/rank_diff.ps1 -Mode template -Out "novels/<书名>/00-radar/2026-11-10.csv"
powershell -ExecutionPolicy Bypass -File scripts/rank_diff.ps1 -Mode diff -Old <旧.csv> -New <新.csv> -Out <报告.md>
powershell -ExecutionPolicy Bypass -File scripts/rank_diff.ps1 -Mode tags -New <快照.csv> -Out <报告.md>
```

脚本输出是**提示，不是判决**：命中 AI 味词不等于必须删除，由总控结合上下文判断。

---

## 七、边界与禁区

- **数据采集**：只用公开可见页面的人工浏览记录（可用 `/browser`）、用户自己的作者后台数据或用户手动整理的数据。**不做**字体反混淆、APP 协议签名模拟等绕过平台防护的抓取。
- **拆解原则**："借骨不借肉"——学结构、节奏、钩子机制，不复制文字、人名、独创设定；拆解文本须由用户合法获取。
- **内容底线**：遵守 [05-fanqie-compliance.md](references/05-fanqie-compliance.md)，平台规则以番茄作家后台最新《内容规范》为准。
- **经验数据声明**：参考文件中的字数、比例、章节节点均为行业经验值，不是平台官方标准。
