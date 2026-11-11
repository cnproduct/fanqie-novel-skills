#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钩子轮换合规检查：扫描 novels/[书名]/ 下所有 第XX章-*.md，
读取每章标注的钩子类型（来自 ## 本章概要 的「悬念钩子」或 ### 章节备注 的「钩子标记/本章悬念」），
校验：① 相邻章不得同型；② 每5章单元内无连续同型；③ 类型分布均衡度。

用法：
  python hook_rotation_check.py <小说目录>

依赖：标准库（os/re/glob/sys）
"""
import os
import re
import sys
import glob
from collections import Counter, OrderedDict

CHAPTER_FILE_RE = re.compile(r'第(\d+)章')
# 显式代号：括号内 / 后接类型词 / 钩子关键词后紧跟
EXPLICIT = re.compile(
    r'[\[（(]([ABCD收])[\]）)]'
    r'|([ABCD收])(?=信息差|危机|关系|身份|收束)'
    r'|(?:钩子标记|钩子类型|钩子|悬念钩子|本章悬念)[：:\s]*([ABCD收])'
)
# 兜底：完整类型短语推断（避免单字误判）
INFER = [
    (re.compile(r'收束|留白'), '收'),
    (re.compile(r'信息差'), 'A'),
    (re.compile(r'危机'), 'B'),
    (re.compile(r'关系转折'), 'C'),
    (re.compile(r'身份揭秘'), 'D'),
]


def extract_meta(path):
    """只抽取元数据区：## 本章概要（到 ## 正文 前）与 ### 章节备注（到文末/下一个---）。"""
    text = open(path, encoding='utf-8').read()
    overview = ''
    m = re.search(r'##\s*本章概要\s*\n(.*?)\n##\s*正文', text, re.S)
    if m:
        overview = m.group(1)
    notes = ''
    m = re.search(r'###\s*章节备注\s*\n(.*?)(?:\n---|\Z)', text, re.S)
    if m:
        notes = m.group(1)
    return overview + "\n" + notes


def extract_hook(path):
    """返回钩子代号 A/B/C/D/收，找不到返回 None。严格只看元数据区。"""
    meta = extract_meta(path)
    # 1) 显式代号
    for line in meta.splitlines():
        if any(k in line for k in ('悬念钩子', '钩子标记', '钩子类型', '钩子：', '钩子:', '本章悬念')):
            m = EXPLICIT.search(line)
            if m:
                return m.group(1) or m.group(2) or m.group(3)
    m = EXPLICIT.search(meta)
    if m:
        return m.group(1) or m.group(2) or m.group(3)
    # 2) 完整类型短语兜底推断
    for pat, code in INFER:
        if pat.search(meta):
            return code
    return None


def main():
    if len(sys.argv) < 2:
        print("用法: python hook_rotation_check.py <小说目录>")
        sys.exit(1)
    base = sys.argv[1]
    files = glob.glob(os.path.join(base, '第*章*.md'))
    # 仅保留确为章节文件的（含「第N章」）
    files = [f for f in files if CHAPTER_FILE_RE.search(os.path.basename(f))]
    if not files:
        print("未找到 第*章*.md 文件，请确认目录路径。")
        sys.exit(1)
    # 按整数章号排序（关键：避免 第100章 排在 第10章 前）
    files.sort(key=lambda f: int(CHAPTER_FILE_RE.search(os.path.basename(f)).group(1)))

    seq = OrderedDict()
    for f in files:
        ch = int(CHAPTER_FILE_RE.search(os.path.basename(f)).group(1))
        seq[ch] = extract_hook(f)

    missing = [c for c, h in seq.items() if h is None]
    print("章数:", len(seq))
    if missing:
        print("⚠️ 未识别到钩子标注的章:", missing)

    dist = Counter(h for h in seq.values() if h)
    print("\n--- 钩子类型分布 ---")
    for k in ['A', 'B', 'C', 'D', '收']:
        print("  %s: %d" % (k, dist.get(k, 0)))

    print("\n--- 相邻同型检查 ---")
    items = list(seq.items())
    adj_viol = []
    for i in range(1, len(items)):
        c0, h0 = items[i - 1]
        c1, h1 = items[i]
        if h0 and h1 and h0 == h1:
            adj_viol.append((c0, c1, h0))
    if adj_viol:
        for c0, c1, h in adj_viol:
            print("  ⚠️ 第%d章 与 第%d章 同为 %s" % (c0, c1, h))
    else:
        print("  ✅ 无相邻同型")

    print("\n--- 5章单元内连续同型检查 ---")
    chapters = list(seq.keys())
    unit_viol = []
    for start in range(0, len(chapters), 5):
        unit = chapters[start:start + 5]
        prev = None
        for c in unit:
            h = seq[c]
            if h and prev and h == prev:
                unit_viol.append((c - 1, c, h))
            prev = h
    if unit_viol:
        for c0, c1, h in unit_viol:
            print("  ⚠️ 单元内 第%d章 与 第%d章 同为 %s" % (c0, c1, h))
        units = max(1, len(chapters) // 5)
        print("  合规率: %.0f%%" % (100 * (1 - len(unit_viol) / units)))
    else:
        print("  ✅ 100% 合规（无单元内连续同型）")


if __name__ == '__main__':
    main()
