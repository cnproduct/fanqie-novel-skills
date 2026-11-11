/**
 * 番茄小说作家后台章节发布与审核状态核验脚本
 * 适用场景：发布/更新后自动化回查所有章节状态，确认全部处于“已发布”，若有“审核不通过”输出具体行
 */
export async function verifyChapterStatus(options = {}) {
  const {
    taskSpaceId = 292,
    bookId
  } = options;

  if (!bookId) {
    throw new Error("必须提供 bookId！");
  }

  const task = await claimTaskSpace(taskSpaceId);
  const page = task.page('writer_page') || task.page('fq_page') || (await task.pages())[0];

  const manageUrl = `https://fanqienovel.com/main/writer/chapter-manage/${bookId}`;
  await page.goto(manageUrl);
  await page.waitForTimeout(3000);

  const report = await page.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('.arco-table-tr')).slice(1);
    const chapters = rows.map(tr => {
      const tds = Array.from(tr.querySelectorAll('td'));
      const titleLink = tr.querySelector('a');
      const title = tds[0]?.innerText?.trim() || '';
      const wordCount = tds[1]?.innerText?.trim() || '';
      const typoCount = tds[2]?.innerText?.trim() || '';
      const status = tds[3]?.innerText?.trim() || '';
      const publishTime = tds[4]?.innerText?.trim() || '';
      const href = titleLink?.getAttribute('href') || '';
      const itemIdMatch = href.match(/publish\/([0-9]+)/) || href.match(/preview\/[0-9]+&([0-9]+)/);
      const itemId = itemIdMatch ? itemIdMatch[1] : '';

      return {
        title,
        wordCount,
        typoCount,
        status,
        publishTime,
        itemId
      };
    });

    const hasFailed = chapters.some(c => c.status.includes('不通过') || c.status.includes('失败'));
    const allPublished = chapters.length > 0 && chapters.every(c => c.status.includes('已发布'));

    return {
      total: chapters.length,
      allPublished,
      hasFailed,
      chapters
    };
  });

  console.log(`\n=== 作品 ${bookId} 章节审核状态核验结果 ===`);
  console.log(`章节总数: ${report.total} | 全部已发布: ${report.allPublished ? '✅ 是' : '❌ 否'}`);
  console.table(report.chapters);

  return report;
}
