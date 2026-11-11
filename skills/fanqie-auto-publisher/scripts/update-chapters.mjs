import fs from 'fs';
import path from 'path';

/**
 * 番茄小说作家后台章节原位修订与重传更新脚本
 * 适用场景：精修文本重新提交、修复“审核不通过”章节
 */
export async function updateChapters(options = {}) {
  const {
    taskSpaceId = 292,
    bookId,
    chapters = [] // 数组项: { num: 1, itemId: '...', txtPath: '...' }
  } = options;

  if (!bookId || chapters.length === 0) {
    throw new Error("必须提供 bookId 和待更新的 chapters 列表！");
  }

  console.log(`=== 开始原位更新作品 ${bookId} 的 ${chapters.length} 个章节 ===`);
  const task = await claimTaskSpace(taskSpaceId);
  const page = task.page('writer_page') || task.page('fq_page') || (await task.pages())[0];

  for (const chap of chapters) {
    console.log(`\n>>> 正在更新第 ${chap.num} 章 (ItemId: ${chap.itemId}) ...`);
    const rawText = fs.readFileSync(chap.txtPath, 'utf-8');
    const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    const titleLine = lines[0];
    const chapterTitle = titleLine.split('：')[1] || titleLine;
    const paragraphs = lines.slice(1);
    const htmlContent = paragraphs.map(p => `<p>${p}</p>`).join('');

    const targetUrl = `https://fanqienovel.com/main/writer/${bookId}/publish/${chap.itemId}/?enter_from=modifychapter`;
    await page.goto(targetUrl);
    await page.waitForTimeout(2500);

    // 1. 设置章节序号与标题（使用 native setter）
    await page.evaluate((data) => {
      function setNativeValue(element, value) {
        const valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
        const prototype = Object.getPrototypeOf(element);
        const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
        if (valueSetter && valueSetter !== prototypeValueSetter) {
          prototypeValueSetter.call(element, value);
        } else {
          valueSetter.call(element, value);
        }
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        element.dispatchEvent(new Event('blur', { bubbles: true }));
      }
      const numInput = document.querySelector('.serial-input.byte-input:not(.serial-editor-input-hint-area)');
      if (numInput) setNativeValue(numInput, String(data.num));
      const titleInput = document.querySelector('input[placeholder="请输入标题"]');
      if (titleInput) setNativeValue(titleInput, data.title);
    }, { num: chap.num, title: chapterTitle });

    await page.waitForTimeout(500);

    // 2. 注入精修正文
    await page.evaluate((html) => {
      const pm = document.querySelector('.ProseMirror');
      if (pm) {
        pm.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertHTML', false, html);
      }
    }, htmlContent);

    await page.waitForTimeout(1500);

    // 3. 点击【下一步】
    await page.evaluate(() => {
      const nextBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '下一步');
      if (nextBtn) nextBtn.click();
    });

    await page.waitForTimeout(1500);

    // 4. 循环处理三级弹窗确认
    for (let step = 0; step < 6; step++) {
      const actionTaken = await page.evaluate(() => {
        // 错别字弹窗
        const errModal = document.querySelector('.auto-editor-error-modal');
        if (errModal && errModal.offsetParent !== null) {
          const sub = Array.from(errModal.querySelectorAll('button')).find(b => b.textContent.trim() === '提交');
          if (sub) { sub.click(); return 'clicked_error_submit'; }
        }
        // 检测方式弹窗
        const checkModal = Array.from(document.querySelectorAll('.arco-modal')).find(m => m.textContent.includes('请选择内容检测方式'));
        if (checkModal && checkModal.offsetParent !== null) {
          const btn = Array.from(checkModal.querySelectorAll('button')).find(b => b.textContent.includes('基础检测') || b.textContent.includes('全面检测'));
          if (btn) { btn.click(); return 'clicked_check_mode'; }
        }
        // 发布设置最终确认
        const pubModal = Array.from(document.querySelectorAll('.arco-modal')).find(m => m.textContent.includes('发布设置'));
        if (pubModal && pubModal.offsetParent !== null) {
          const labels = Array.from(pubModal.querySelectorAll('label, .arco-radio, input[type="radio"]'));
          const yesLabel = labels.find(l => l.textContent.includes('是'));
          if (yesLabel) yesLabel.click();
          const conf = Array.from(pubModal.querySelectorAll('button')).find(b => b.textContent.includes('确认提交') || b.textContent.includes('确认发布'));
          if (conf) { conf.click(); return 'clicked_final_confirm'; }
        }
        return 'none';
      });
      if (actionTaken === 'clicked_final_confirm') break;
      await page.waitForTimeout(1200);
    }

    await page.waitForTimeout(2500);
    console.log(`第 ${chap.num} 章更新并提交成功！`);
  }

  console.log("\n🎉 全量章节原位更新完毕！");
}
