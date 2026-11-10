# fanqie-auto-publisher

番茄小说作家后台全自动发书与章节上传 Agent Skill。

---

## 概述

`fanqie-auto-publisher` 是专门针对番茄小说（Fanqie Novel）原创文学平台的自动化发书总控。配合 `ego lite` 浏览器环境，可在作者登录状态下，全自动完成：

- **作品元数据格式化**（严格遵循 15 字书名、分类标签配额、高转化简介模版）
- **内置封面自适应渲染与选定**
- **连载模式 / 完本模式 智能适配与平台限额探测**
- **批量纯文本章节清洗与逐章上传发布**

---

## 目录结构

```
fanqie-auto-publisher/
├── SKILL.md                          # 技能规范与总控流程定义
├── README.md                         # 模块说明与快速指引
├── scripts/
│   └── publish-to-fanqie.mjs         # 生产级自动化发布执行脚本
└── references/
    ├── 01-fanqie-platform-rules.md   # 番茄平台发书限制与字段规范手册
    └── 02-browser-automation.md      # ego-browser 自动化接管接口速查
```

---

## 快速使用

在已登录番茄作家专区（`https://fanqienovel.com/main/writer/home`）的终端执行：

```powershell
& "C:\Program Files\Citro Labs\ego lite\Application\0.6.2.7\ego-browser.exe" nodejs -e "await import('file:///C:/Users/Admin/.gemini/config/plugins/fanqie-novel-skills/skills/fanqie-auto-publisher/scripts/publish-to-fanqie.mjs')"
```

---

## 许可证

MIT License
