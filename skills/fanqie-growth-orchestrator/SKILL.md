---
name: fanqie-growth-orchestrator
description: >-
  番茄小说成长向总控引擎（真我与良知的精神食粮）。保留番茄的追读力（钩子、节奏、白描、黄金三章），
  但把兑现物从"欲望满足"升级为"内在觉醒"：读者以欲望入场，在主角付出代价、做出选择的过程中照见真我、唤醒良知。
  核心公式："真实困境 × 错误信念被代价击碎 × 主动选择 × 良知回响"。按 G0-G8 状态机推进：
  心灵雷达 → 立意与反命题 → 灵魂账本 → 双线成长弧大纲 → 黄金三章 → 逐章连载 → 追读力与精神价值双重审计 → 读者回响复盘。
  需要扫榜、黄金三章、文本体检时调用 fanqie-hit-orchestrator 的参考与脚本；人物与主题深度调用 screenwriting-skills。
  当用户要写成长、励志、治愈、现实向、修心、家庭、职场、年代、历史人物等"让人变好"的网文，
  或要求给爽文"加魂"、去鸡汤、去说教时使用。
---

# 番茄小说成长向总控引擎（Fanqie Growth Orchestrator）

> **定位**：精神食粮，不是鸡汤。让读者在追读的快感里，照见自己、看清自己、愿意成为更好的自己。
> **核心公式**：`成长 = 真实困境 × 错误信念被代价击碎 × 主动选择 × 良知回响`
> **方法总纲**：**以钩引心，以爽载道**——欲望是入口，觉醒是出口。

本技能是**总控**：负责流程、记忆、调度和闸口。番茄平台的追读技术（扫榜、黄金三章、章尾钩、文本体检）**直接复用 `fanqie-hit-orchestrator`**，本技能专注"魂"的部分。

---

## 一、五条铁律

1. **不说教**：主题只能被行动证明，不能被台词宣布。人物越想讲道理，作者越要让他闭嘴（见 [04-anti-preachiness.md](references/04-anti-preachiness.md)）。
2. **成长必须付代价**：没有代价的顿悟就是鸡汤。觉醒之前，主角必须因错误信念真实地失去过什么。
3. **先接住欲望，再转化欲望**：读者想要变强、被认可、复仇，这些不是敌人，而是入口。不批判读者，只带他走得更远（见 [01-inner-need-map.md](references/01-inner-need-map.md)）。
4. **反命题要有力量**：对手、诱惑、"另一条路"必须有真实的说服力。反命题越强，主题越可信。
5. **良知不等于道德正确**：允许灰度、犯错、迟疑、倒退。良知是人物在关键时刻听见自己内心的声音，而不是作者替他做的正确选择。

> **思想锚点（作为创作框架借用）**：王阳明"致良知 / 知行合一 / 事上磨练"；荣格"自性化"（成为真正的自己）；Lisa Cron"错误信念"；Truby"道德需求"；契诃夫"不评判人物"；小津"日常中见真"。

---

## 二、项目目录约定

与 `fanqie-hit-orchestrator` 一致（`novels/<书名>/`，`state.md` 为唯一真相源，模板见 `../fanqie-hit-orchestrator/templates/state.md`，填写其中的"成长向"字段），另增：

```
novels/<书名>/01-bible/soul-bible.md     # 灵魂账本（模板：templates/soul-bible.md）
novels/<书名>/02-outline/growth-outline.md  # 双线成长弧大纲（模板：templates/growth-outline.md）
```

---

## 三、阶段状态机（G0-G8）

| 阶段 | 触发 | 核心动作 | 调度 | 产出 | 闸口 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **G0 读档/建档** | 每次调用 | 读取或创建 `state.md`，判断阶段 | `../fanqie-hit-orchestrator/templates/state.md` | state.md | 阶段明确 |
| **G1 心灵雷达** | `/pulse` "现在读者心里缺什么" | **双雷达**：① 榜单雷达（复用 hit 的 P1）；② 心灵痛点雷达（书评区、高赞评论、社会话题中的集体情绪） | `../fanqie-hit-orchestrator/references/06-trend-radar.md`、`rank_diff.ps1`、[01-inner-need-map.md](references/01-inner-need-map.md) 第三节 | 心灵痛点报告 | 每个痛点有来源 |
| **G2 立意与反命题** | `/theme` | 找到"入口欲望 → 深层需要 → 主题命题 → 反命题"，测试 logline | [01-inner-need-map.md](references/01-inner-need-map.md)、`sw-premise-theme`（控制观念 = 价值 + 原因） | 立意卡 ×2-3 | **用户选定**；反命题有说服力 |
| **G3 灵魂账本** | `/soul` | 主角的创伤/错误信念/欲望/需要/良知触发点；镜像人物；对手的正当逻辑 | [templates/soul-bible.md](templates/soul-bible.md)、`sw-truby-anatomy`（道德需求）、`sw-character-conflict`、`chekhov-dramaturgy`；金手指部分调 hit 的 `04-cheat-and-progression.md` | `soul-bible.md` | 错误信念具体可演；对手不是纸片人 |
| **G4 成长弧大纲** | `/arc` | 迷→觉→行→合四阶；外部爽点线 × 内部觉点线**双线对位**；每卷一次"信念崩塌与重建" | [02-growth-arc.md](references/02-growth-arc.md)、`sw-story-structure`、`sw-series-engine-bible`；节奏调 hit 的 `03-chapter-engine.md` | `growth-outline.md` | 每个觉点都对应一个外部事件和代价 |
| **G5 黄金三章** | `/open` | 入口仍是欲望/危机，同时埋下"内在裂缝" | hit 的 `02-golden-three-chapters.md` + [03-hook-with-meaning.md](references/03-hook-with-meaning.md) | 第 001-003 章 | hit 三章自检表 + 裂缝已埋 |
| **G6 逐章连载** | `/write [N]` | 单章四段：承钩 → 事上磨练 → 选择时刻 → 余味 + 新钩 | [03-hook-with-meaning.md](references/03-hook-with-meaning.md)、`sw-scene-craft`、`sw-dialogue`（潜台词）、`ozu-screenplay-style`（日常戏） | 第 N 章 + 更新 state.md | 一钩一觉（或一钩一裂缝）；无说教红灯 |
| **G7 双重审计** | `/audit` 或每 10 章 | **追读力轴**（hit 审计）+ **精神价值轴**（良知标尺）+ 去说教扫描 | hit 的 `text_lint.ps1` 叠加 `scripts/lexicons/preachy.txt`、[05-conscience-audit.md](references/05-conscience-audit.md)、[04-anti-preachiness.md](references/04-anti-preachiness.md)、`anti-template-repair.md`、`screenwriter-skill` 铁律 | 双轴审计报告（[模板](templates/dual-audit-report.md)） | **两轴均 ≥ B**，无红线 |
| **G8 读者回响复盘** | `/echo` | 分析评论区：被戳中、引发反思、"我也是这样"类反馈 vs 弃书点 | [05-conscience-audit.md](references/05-conscience-audit.md) 第四节 | 复盘结论 + 大纲修订 | — |

---

## 四、快捷指令

| 指令 | 作用 |
| :--- | :--- |
| `/pulse [人群/题材]` | 心灵痛点雷达（G1） |
| `/theme [想法]` | 立意卡：入口欲望 → 深层需要 → 命题 / 反命题（G2） |
| `/soul` | 灵魂账本（G3） |
| `/arc` | 双线成长弧大纲（G4） |
| `/open`、`/write [N]` | 黄金三章 / 逐章（G5-G6） |
| `/deepen <章节>` | 给已有爽文章节"加魂"：找到可转化的爽点，改写为觉点（不减爽感） |
| `/depreach <章节>` | 去说教改写 |
| `/audit [范围]` | 双重审计（G7） |
| `/echo` | 读者回响复盘（G8） |
| `/status` | 进度 + 主角当前信念状态 + 未回收伏笔 |

---

## 五、子技能调度表（路径相对本技能目录）

| 子技能 / 文件 | 何时加载 | 用途 |
| :--- | :--- | :--- |
| `../fanqie-hit-orchestrator/references/06-trend-radar.md`、`scripts/rank_diff.ps1` | G1 | 榜单雷达 |
| `../fanqie-hit-orchestrator/references/02-golden-three-chapters.md` | G5 | 黄金三章技术 |
| `../fanqie-hit-orchestrator/references/03-chapter-engine.md` | G4、G6 | 章节节奏与钩型 |
| `../fanqie-hit-orchestrator/references/04-cheat-and-progression.md` | G3（有金手指时） | 金手指四要素 |
| `../fanqie-hit-orchestrator/references/05-fanqie-compliance.md` | G7 | 合规 |
| `../fanqie-hit-orchestrator/scripts/text_lint.ps1` | G7 | 文本体检 + 说教词库 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-premise-theme/` | G2 | 命题、控制观念、logline |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-truby-anatomy/` | G3 | 心理需求与道德需求 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-character-conflict/` | G3 | 人物冲突网 |
| `../screenwriting-skills/plugins/screenwriting/skills/chekhov-dramaturgy/` | G3、G6 | 不评判、灰度人物、潜流 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-story-structure/` | G4 | 结构 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-series-engine-bible/` | G4 | 长篇连载引擎 |
| `../screenwriting-skills/plugins/screenwriting/skills/sw-scene-craft/`、`sw-dialogue/` | G6 | 场景价值翻转、潜台词 |
| `../screenwriting-skills/plugins/screenwriting/skills/ozu-screenplay-style/` | G6（日常/家庭戏） | 生活流、留白 |
| `../zenstory-drama-skills/skills/short-drama-review/references/anti-template-repair.md` | G7 | 反套路修复 |
| `../screenwriter-skill/references/iron_rules.md` | G7 | 主编铁律 |
| `../script-super-orchestrator/` | 网文 → 剧本改编 | 下游 |

---

## 六、工具用法

```powershell
# 文本体检 + 说教词库（在本技能目录下执行）
powershell -ExecutionPolicy Bypass -File ../fanqie-hit-orchestrator/scripts/text_lint.ps1 -Path "novels/<书名>/03-chapters/第010章.md" -Lexicon "scripts/lexicons/preachy.txt" -Out "novels/<书名>/04-audit/lint-010.md"
```

说教词命中只是提醒：角色反讽、对手说出的"大道理"可以保留；作者旁白和主角顿悟独白里的命中需要重点改写。

---

## 七、与爆款总控的协作模式

| 模式 | 适用 | 主控 | 方式 |
| :--- | :--- | :--- | :--- |
| **纯成长向** | 现实、治愈、励志、年代、家庭 | growth | 只借 hit 的追读技术 |
| **爽中有魂**（推荐给番茄） | 修仙修心、重生、系统、逆袭 | growth | 外部爽点线按 hit 标准设计，内部觉点线由 growth 把关 |
| **爽文加魂** | 已有爽文想提质 | hit → `/to-growth` | growth 执行 `/deepen`，不删爽点，只把部分爽点升级为觉点 |

---

## 八、边界

- 数据采集与拆解遵循 `fanqie-hit-orchestrator` 第七节的边界（不绕过平台防护，借骨不借肉）。
- 不以"成长"之名贩卖焦虑、成功学或道德优越感（见 [05-conscience-audit.md](references/05-conscience-audit.md) 红线）。
- 不替读者下结论：作品提供镜子，不提供标准答案。
