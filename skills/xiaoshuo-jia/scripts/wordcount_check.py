#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字数纪律检查：扫描 novels/[书名]/ 下所有 第XX章-*.md，
抽取 ## 正文 到 --- 之间的正文，统计 CJK 字数并报告纪律指标。

用法：
  python wordcount_check.py <小说目录> [--volumes "1-15,16-35,36-65,66-85,86-100"]

依赖：标准库（os/re/glob/statistics/sys）
输出：章数、均值、中位、最小/最大、标准差、超标章、分卷均字（若提供 --volumes）
"""
import os
import re
import sys
import glob
import statistics

CJK = re.compile(r'[一-鿿]')
CHAPTER_RE = re.compile(r'第(\d+)章')
BODY_RE = re.compile(r'##\s*正文\s*\n(.*?)\n---', re.S)
LOW, HIGH = 2200, 2800


def extract_body(path):
    text = open(path, encoding='utf-8').read()
    m = BODY_RE.search(text)
    return m.group(1) if m else text


def main():
    if len(sys.argv) < 2:
        print("用法: python wordcount_check.py <小说目录> [--volumes \"1-15,16-35,...\"]")
        sys.exit(1)
    base = sys.argv[1]
    volumes = None
    if '--volumes' in sys.argv:
        idx = sys.argv.index('--volumes')
        volumes = sys.argv[idx + 1]

    files = sorted(glob.glob(os.path.join(base, '第*章-*.md')))
    if not files:
        print("未找到 第*章-*.md 文件，请确认目录路径。")
        sys.exit(1)

    counts = {}
    for f in files:
        body = extract_body(f)
        n = len(CJK.findall(body))
        m = CHAPTER_RE.search(os.path.basename(f))
        ch = int(m.group(1)) if m else len(counts) + 1
        counts[ch] = n

    vals = list(counts.values())
    print("章数:", len(vals))
    print("均值: %.1f" % statistics.mean(vals))
    print("中位:", statistics.median(vals))
    print("最小:", min(vals), " 最大:", max(vals))
    print("标准差: %.1f" % statistics.pstdev(vals))
    out = [c for c in vals if c < LOW or c > HIGH]
    print("超标章(<%d 或 >%d):" % (LOW, HIGH), out if out else "无")

    if volumes:
        print("\n--- 分卷均字 ---")
        for seg in volumes.split(','):
            seg = seg.strip()
            if '-' not in seg:
                continue
            a, b = seg.split('-')
            rng = range(int(a), int(b) + 1)
            vs = [counts[c] for c in rng if c in counts]
            if vs:
                print("  %s-%s: 均字 %.1f (n=%d)" % (a, b, statistics.mean(vs), len(vs)))


if __name__ == '__main__':
    main()
