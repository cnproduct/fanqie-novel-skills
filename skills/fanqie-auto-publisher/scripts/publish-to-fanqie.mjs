import fs from 'fs';
import path from 'path';

/**
 * 番茄小说作家后台全自动发书与章节上传脚本
 * 支持 ego lite 动态接管、表单合规清洗、自适应封面生成与限额检测
 */
export async function publishNovel(novelConfig = {}) {
  const defaults = {
    title: "重生1983靠修收音机整顿全家",
    gender: "0", // 0: 女频, 1: 男频
    mainCategory: "年代",
    readingTags: ["年代", "发家致富", "重生"],
    contentTags: ["无CP"],
    role1: "许青禾",
    role2: "",
    intro: `1983年冬，母亲逼我签字放弃顶替名额换彩礼？我当场让出必倒闭的破工厂名额，带走坏收音机。
三十年维修手艺在脑，从修好第一台飞燕牌收音机开始，摆地摊、换粮票、斗极品、创实业！
偏心母亲哭着求我接济，弟弟眼红下跪认错，全县百货争着抢我的货。
这一世，我不靠任何人，靠自己的双手和手艺，不仅整顿全家，更要堂堂正正活成万元户、行业第一人！`
  };

  const config = { ...defaults, ...novelConfig };
  console.log("=== 番茄小说自动创建与发布流程启动 ===");

  const task = await takeOverTaskSpace(0);

  let page;
  try {
    page = task.page("writer_page");
  } catch (e) {
    const tabs = await task.tabs();
    for (const t of tabs) {
      if (t.url.includes("fanqienovel.com")) {
        page = await task.adopt(t.page, { as: "writer_page" });
        break;
      }
    }
  }

  if (!page) {
    throw new Error("未检测到番茄小说后台标签页，请确保在 ego lite 中已打开作家专区！");
  }

  console.log("导航至作品创建页...");
  await page.goto("https://fanqienovel.com/main/writer/create");
  await page.waitForTimeout(3000);

  // 关闭签约说明等遮罩弹窗
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent.includes('知道了') || b.getAttribute('aria-label') === 'Close');
    if (btn) btn.click();
  });
  await page.waitForTimeout(1000);

  // 选择频道 (0: 女频, 1: 男频)
  await page.evaluate((val) => {
    const radio = document.querySelector(`input[type="radio"][value="${val}"]`);
    if (radio) radio.click();
  }, config.gender);
  console.log(`频道设定: ${config.gender === '0' ? '女频' : '男频'}`);
  await page.waitForTimeout(1000);

  // 填写书名 (限15字符)
  const trimmedTitle = config.title.slice(0, 15);
  await page.fill('input[placeholder="请输入作品名称"]', trimmedTitle);
  console.log(`书名填写: ${trimmedTitle}`);

  // 配置阅读标签
  console.log("配置阅读标签...");
  await page.evaluate(() => {
    const views = Array.from(document.querySelectorAll('.select-view'));
    if (views[0]) views[0].click();
  });
  await page.waitForTimeout(1500);

  await page.evaluate((tags) => {
    const modal = Array.from(document.querySelectorAll('.arco-modal')).find(m => m.textContent.includes('阅读标签'));
    if (!modal) return;
    const items = Array.from(modal.querySelectorAll('.category-choose-item'));
    for (const t of tags) {
      const it = items.find(el => el.textContent.trim() === t);
      if (it) it.click();
    }
    const confirmBtn = Array.from(modal.querySelectorAll('button')).find(b => b.textContent.trim() === '确认');
    if (confirmBtn) confirmBtn.click();
  }, config.readingTags);
  await page.waitForTimeout(1500);

  // 配置内容标签
  console.log("配置内容标签...");
  await page.evaluate(() => {
    const views = Array.from(document.querySelectorAll('.select-view'));
    if (views[1]) views[1].click();
  });
  await page.waitForTimeout(1500);

  await page.evaluate((tags) => {
    const modal = Array.from(document.querySelectorAll('.arco-modal')).find(m => m.textContent.includes('内容标签'));
    if (!modal) return;
    const items = Array.from(modal.querySelectorAll('.category-choose-item, .category-choose-item-title, span, div'))
      .filter(el => el.children.length === 0 && tags.includes(el.textContent.trim()));
    for (const it of items) it.click();
    const confirmBtn = Array.from(modal.querySelectorAll('button')).find(b => b.textContent.trim() === '确认');
    if (confirmBtn) confirmBtn.click();
  }, config.contentTags);
  await page.waitForTimeout(1500);

  // 填写主角名
  await page.fill('input[placeholder="请输入主角名1"]', config.role1);
  if (config.role2) {
    await page.fill('input[placeholder="请输入主角名2"]', config.role2);
  }
  console.log(`主角设定: ${config.role1}`);

  // 填写简介
  await page.fill('textarea[placeholder*="请输入50-500字以内的作品简介"]', config.intro.trim());
  console.log(`简介填写完毕 (${config.intro.trim().length} 字)`);

  // 封面生成 (模板自适应封面)
  console.log("自动渲染模板封面...");
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('选择封面'));
    if (btn) btn.click();
  });
  await page.waitForTimeout(1500);

  await page.evaluate(() => {
    const tabs = Array.from(document.querySelectorAll('[role="tab"], .arco-tabs-header-cell'));
    const t = tabs.find(x => x.textContent.includes('模板封面'));
    if (t) t.click();
  });
  await page.waitForTimeout(1500);

  await page.evaluate(() => {
    const modal = document.querySelector('.arco-modal:last-of-type') || document.body;
    const canvas = modal.querySelector('canvas');
    if (canvas) canvas.click();
  });
  await page.waitForTimeout(800);
  await page.click('text=确定');
  await page.waitForTimeout(2000);

  // 提交建书
  console.log("提交创建作品...");
  await page.click('text=立即创建');
  await page.waitForTimeout(4000);

  const currentUrl = await page.url();
  const snap = await page.snapshot();

  if (snap.includes("创建完本模式作品数超出每日上限")) {
    console.warn("\n⚠️ 平台提示: 【创建完本模式作品数超出每日上限】");
    console.warn("说明: 番茄平台单账号每日限创 1 部完本作品。明日 00:00 额度将自动恢复。");
    return { success: false, reason: "daily_limit_reached" };
  }

  if (currentUrl.includes("/book-info/")) {
    const bookId = currentUrl.split("/book-info/")[1].split("?")[0];
    console.log(`\n🎉 书籍创建成功！BookId: ${bookId}`);
    return { success: true, bookId };
  }

  return { success: false, currentUrl };
}

// 默认直接执行
publishNovel().catch(console.error);
