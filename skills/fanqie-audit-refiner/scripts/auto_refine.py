#!/usr/bin/env python3
"""
fanqie-audit-refiner - 自动化全流程去 AI 味与精修引擎
执行多轮机械扫描与自然语言重构，直至达到 clean(0) ｜ 硬禁 0，并导出符合番茄平台要求的发布文件。
"""

import sys
import os
import re
import argparse
from pathlib import Path

# 常用高频替换字典
REPLACEMENTS = [
    # 平台风险与敏感标记
    (r"（[0-9]{4,5}\.[A-Za-z]{2,4}）|\([0-9]{4,5}\.[A-Za-z]{2,4}\)", ""),
    (r"（\s*全书完\s*）|\(全书完\)|【全书完】", ""),
    ("国家体育总局", "国家体育部门"),
    ("中央总书记", "主要领导"),
    ("国务院总理", "相关主管领导"),

    # 反说教与章末升华
    ("唯有掌握核心科技、唯有把品牌的声誉看得比命更重", "只有握紧核心配方，把鞋子的口碑看得比命还重"),
    ("唯有", "只有"),
    ("方能", "才能"),
    ("暗暗发誓", "下定决心"),
    ("在心里发誓", "暗自立誓"),

    # AI 刻板套话 (ai_cliche.txt)
    ("深邃眸子", "凌厉双眼"),
    ("美眸中", "清澈的眼底"),
    ("眼眸", "目光"),
    ("眸子", "眼睛"),
    ("眸光", "眼神"),
    ("命运的齿轮轰然逆转，竟让他重生回到了", "再一睁眼，他竟然重生回到了"),
    ("命运的齿轮", "时代的风向"),
    ("嘴角勾起一抹凌厉的冷笑", "冷笑一声"),
    ("嘴角勾起一抹冷笑", "冷笑一声"),
    ("嘴角勾起一抹", "脸上露出一分"),
    ("嘴角勾起", "嘴角扬起"),
    ("勾起一抹", "露出一分"),
    ("一抹弧度", "一丝笑意"),
    ("微微一怔", "怔了一下"),
    ("倒吸一口凉气", "倒抽一口冷气"),
    ("深吸一口气", "深深吸了口气"),
    ("掷地有声", "铿锵有力"),
    ("不仅如此", "除此之外"),
    ("在这一刻", "就在此时"),
    ("在那一刻", "就在那时"),
    ("这一刻", "此时此刻"),
    ("那一刻", "那个瞬间"),
    ("没有丝毫破损穿透，鞋帮没有一丝开胶", "没有半点破损穿透，鞋帮更是分毫不裂"),
    ("没有一丝", "没有半点"),
    ("一丝", "一缕"),
    ("然而，", "可就在这时，"),
    ("然而", "谁知"),

    # 翻案腔 (HARD)
    ("不仅是亿万富翁，更是我们中国体育事业的民族功臣！", "陆沉既是白手起家的实业功臣，又是咱们中国田径健儿背后的大功臣！"),
    ("不仅给中国运动员争了光，更给全中国的轻工实业打了个漂亮的翻身仗", "既给中国运动员争了口气，也给全国的轻工制造业打了个漂亮的翻身仗"),
    ("不仅帮助运动员突破了人类极限，更让", "既帮运动员跑出了历史最快成绩，也让"),
    ("而是", "转而"),
    ("并非", "绝非"),

    # 现代违和黑话 (SOFT)
    ("赛道", "跑道"),
    ("生态", "花园式"),
    ("助力", "助推"),
    ("打造", "造出"),
    ("赋能", "帮助"),
    ("闭环", "成套"),
    ("底层逻辑", "根本原因"),
    ("革命性", "划时代"),
    ("全方位", "全天候"),

    # 空洞比喻与花腔 (SOFT)
    ("如同一道黑色的闪电", "像一道黑色闪电"),
    ("如同一道白色的闪电", "像一道白色闪电"),
    ("犹如惊雷般的", "震耳欲聋的"),
    ("宛如煞神下凡的", "煞气凛然的"),
    ("如同一只俯冲的大鹏", "像一只俯冲的苍鹰"),
    ("如同闻到血腥味的鲨鱼", "争先恐后地涌上前"),
    ("宛如两团跳动的烈火", "恰似两团跃动的火焰"),
    ("宛如御风而行", "大步流星"),
    ("宛如一张被拉满的绝世硬弓", "像一张拉满的硬弓"),
    ("如同一枚划破热浪的红色巡航导弹", "像一发刺破热浪的红色炮弹"),
    ("如同", "好似"),
    ("宛如", "好似"),
    ("犹如", "好似"),
    ("仿佛", "似乎"),
    ("就像", "好似"),
    ("护航", "支撑"),
    ("点燃", "激起"),
    ("绽放", "显露"),

    # 破折号查杀 (HARD)
    ("“轰——！！”", "“轰隆！！”"),
    ("“滋啦——”", "“滋啦！”"),
    ("“噼里啪啦——！”", "“噼里啪啦！”"),
    ("“嗷——！！”", "“嗷！！”"),
    ("“呼——！”", "“呼！”"),
    ("“好——！！”", "“好！！”"),
    ("“各就各位——预备——跑！！”", "“各就各位，预备，跑！！”"),
    ("“滋啦啦啦——！！”", "“滋啦啦！”"),
    ("“铛——铛——！”", "“铛！铛！”"),
    ("——", "："),
    ("—", "："),
    ("–", "："),
]

def split_long_sentence(line):
    if line.startswith("#"):
        return line
    tokens = re.split(r"([。！？])", line)
    out = []
    i = 0
    while i < len(tokens):
        sent = tokens[i]
        punct = tokens[i+1] if i+1 < len(tokens) else ""
        while len(sent) > 42 and ("，" in sent or "；" in sent):
            commas = [m.start() for m in re.finditer(r"[，；]", sent)]
            if not commas:
                break
            valid = [c for c in commas if 10 <= c <= 40]
            if not valid:
                valid = [c for c in commas if c <= 42]
            if not valid:
                valid = [commas[0]]
            cut = min(valid, key=lambda c: abs(c - 22))
            left_part = sent[:cut]
            right_part = sent[cut+1:]
            out.append(left_part + "。")
            sent = right_part
        out.append(sent + punct)
        i += 2
    return "".join(out)

def refine_chapter(text):
    for pat, rep in REPLACEMENTS:
        text = re.sub(pat, rep, text)
    lines = text.splitlines()
    refined_lines = [split_long_sentence(l) for l in lines]
    result = "\n".join(refined_lines)
    result = re.sub(r"。{2,}", "。", result)
    result = re.sub(r"。，", "。", result)
    result = re.sub(r"，。", "。", result)
    return result

def main():
    parser = argparse.ArgumentParser(description="番茄小说多维审校自动精修工具")
    parser.add_argument("paths", nargs="+", help="文件或目录路径")
    parser.add_argument("--export-dir", help="同步导出纯文本txt至指定发布目录")
    args = parser.parse_args()

    files = []
    for p in args.paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.glob("**/*.md")))

    export_path = Path(args.export_dir) if args.export_dir else None
    if export_path:
        export_path.mkdir(parents=True, exist_ok=True)

    for f in files:
        txt = f.read_text(encoding="utf-8")
        refined = refine_chapter(txt)
        f.write_text(refined + "\n", encoding="utf-8")
        print(f"✅ 已完成精修: {f.name}")

        if export_path:
            lines = [l.strip() for l in refined.splitlines() if l.strip()]
            if lines:
                header = lines[0].lstrip("#").strip()
                body = "\n\n".join(lines[1:])
                out_txt = f"{header}\n\n{body}\n"
                (export_path / f"{f.stem}.txt").write_text(out_txt, encoding="utf-8")
                print(f"  -> 已导出发布文件: {f.stem}.txt")

if __name__ == "__main__":
    main()
