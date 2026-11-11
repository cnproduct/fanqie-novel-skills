#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布版抽取：扫描 novels/[书名]/ 下所有 第XX章-*.md，
仅抽取 ## 正文 到 --- 之间的正文，按 前导零序号-标题.txt 导出到发布目录。
剥离全部写作元数据（本章概要、章节备注、钩子/伏笔标注）。

用法：
  python strip_metadata.py <小说目录> <输出目录>

依赖：标准库（os/re/glob/sys）
"""
import os
import re
import sys
import glob

CHAPTER_RE = re.compile(r'第(\d+)章-(.+?)\.md$')
BODY_RE = re.compile(r'##\s*正文\s*\n(.*?)\n---', re.S)


def main():
    if len(sys.argv) < 3:
        print("用法: python strip_metadata.py <小说目录> <输出目录>")
        sys.exit(1)
    base = sys.argv[1]
    out_dir = sys.argv[2]
    files = sorted(glob.glob(os.path.join(base, '第*章-*.md')))
    if not files:
        print("未找到 第*章-*.md 文件，请确认目录路径。")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    n = 0
    for f in files:
        m = CHAPTER_RE.search(os.path.basename(f))
        if not m:
            continue
        ch = int(m.group(1))
        title = m.group(2)
        text = open(f, encoding='utf-8').read()
        bm = BODY_RE.search(text)
        body = bm.group(1).strip() if bm else text.strip()
        out_name = "%03d-%s.txt" % (ch, title)
        with open(os.path.join(out_dir, out_name), 'w', encoding='utf-8') as wf:
            wf.write(body + "\n")
        n += 1
    print("已导出 %d 章干净正文到: %s" % (n, out_dir))


if __name__ == '__main__':
    main()
