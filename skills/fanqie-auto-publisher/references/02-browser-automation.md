# ego-browser 自动化接管接口速查手册

## 1. 运行方式

通过 Windows PowerShell 调用 ego-browser 附带的 Node.js 运行环境：

```powershell
& "C:\Program Files\Citro Labs\ego lite\Application\0.6.2.7\ego-browser.exe" nodejs -e "await import('file:///C:/path/to/script.mjs')"
```

## 2. 核心 SDK 模式

```javascript
// 1. 接管指定 TaskSpace
const task = await takeOverTaskSpace(0);

// 2. 识别并收编目标 Tab
const tabs = await task.tabs();
const target = tabs.find(t => t.url.includes("fanqienovel.com"));
const page = await task.adopt(target.page, { as: "writer_page" });

// 3. 元素操作
await page.goto("https://fanqienovel.com/main/writer/create");
await page.fill('input[placeholder="请输入作品名称"]', '书名');
await page.click('text=立即创建');

// 4. 快照探测
const snap = await page.snapshot();
```
