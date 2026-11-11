#!/usr/bin/env python3
"""
fanqie-audit-refiner - 番茄小说全维度专业审校体检引擎
融合技能：
  - write (check.py / patterns-zh.md): 查杀破折号、翻案腔、冒号提示语、黑话宣传语、空洞花腔、长句
  - fanqie-hit-orchestrator: ai_cliche.txt (神态套话/旁白腔) 与 risk_words.txt (合规风控)
  - fanqie-growth-orchestrator: preachy.txt 与 anti-preachiness (反爹味/反章尾升华)
  - fanqie-auto-publisher 平台风控合规矩阵: 真实股票代码/外链正则/国家机关全称/完本标记冲突
"""

import sys
import os
import re
import math
import json
import argparse
from pathlib import Path

# --- 1. write 技能硬禁与软扣分规则 ---
HARD_RULES = {
    "破折号": re.compile(r"——|—|–"),
    "翻案腔": re.compile(
        r"不是[^。！？\n]{1,25}[，,]\s*(而)?是|"
        r"而是|并非|"
        r"不仅[^。！？\n]{0,20}(而且|更是|也是)|"
        r"与其说|不在于[^。！？\n]{0,20}而在于|"
        r"表面[^。！？\n]{0,15}实际|看似[^。！？\n]{0,15}实则|"
        r"你以为[^。！？\n]{0,20}其实|回头才发现|答案恰恰相反|说到底"
    ),
    "提示性冒号": re.compile(
        r"(总结|核心|关键|结论|重点|答案|原因|一句话|简单来说|总之)[是为]?\s*[：:]"
    ),
    "口头路标": re.compile(
        r"(首先|其次|再次|最后|第一[，、]|第二[，、]|一方面|另一方面|换句话说|不可否认的是|毫无疑问的是)[，,]"
    ),
}

SOFT_RULES = {
    "黑话与宣传语": re.compile(
        r"赋能|助力|打造|深耕|抓手|闭环|底层逻辑|颗粒度|沉淀|链路|生态|愿景|全方位|一站式|无缝|革命性|引领|赛道|矩阵"
    ),
    "比喻与花腔": re.compile(
        r"就像|如同|仿佛|好比|堪比|犹如|宛如|画卷|织就|谱写|扬帆|护航|注入[^。\n]{0,4}活力|点燃|绽放"
    ),
    "空洞概括": re.compile(
        r"某种意义上|很大程度上|从长远来看|值得深思|发人深省|耐人寻味|毋庸置疑|显而易见|众所周知"
    ),
}

# --- 2. 平台合规风控硬触发规则 ---
PLATFORM_RISK_RULES = {
    "真实证券代码与域名外链": re.compile(r"（?[0-9]{4,5}\.[A-Za-z]{2,4}）?|https?://[^\s]+|\.com|\.cn|\.hk|\.net"),
    "真实国家领导与敏感公职": re.compile(r"中央总书记|国家主席|国务院总理|省委书记|市委书记|县委书记"),
    "连载中完本标记冲突": re.compile(r"（\s*全书完\s*）|\(全书完\)|【全书完】"),
}

def load_lexicon(file_path):
    if not os.path.exists(file_path):
        return []
    words = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                word = line.split("|")[0].strip()
                if word:
                    words.append(word)
    return words

def get_default_lexicons():
    base_dir = Path(__file__).resolve().parent.parent.parent
    hit_cliche = base_dir / "fanqie-hit-orchestrator" / "scripts" / "lexicons" / "ai_cliche.txt"
    hit_risk = base_dir / "fanqie-hit-orchestrator" / "scripts" / "lexicons" / "risk_words.txt"
    growth_preachy = base_dir / "fanqie-growth-orchestrator" / "scripts" / "lexicons" / "preachy.txt"
    
    return {
        "cliche": load_lexicon(hit_cliche),
        "risk": load_lexicon(hit_risk),
        "preachy": load_lexicon(growth_preachy),
    }

def calc_variation(lengths):
    if not lengths:
        return 0.0
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    return math.sqrt(variance) / mean

def audit_text(text, filename="<text>", lexicons=None):
    if lexicons is None:
        lexicons = get_default_lexicons()

    # 1. 基础字数与结构统计
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    para_lengths = [len(p) for p in paras]
    para_cv = calc_variation(para_lengths)

    # 句切分
    sentences = [s.strip() for s in re.split(r"[。！？\n]+", text) if s.strip()]
    sent_lengths = [len(s) for s in sentences]
    sent_cv = calc_variation(sent_lengths)

    # 超长句统计 (>45字)
    long_sents = [s for s in sentences if len(s) > 45]

    # 2. 规则命中统计
    hard_hits = {}
    for name, pat in HARD_RULES.items():
        matches = pat.findall(text)
        if matches:
            hard_hits[name] = matches

    soft_hits = {}
    for name, pat in SOFT_RULES.items():
        matches = pat.findall(text)
        if matches:
            soft_hits[name] = matches

    platform_hits = {}
    for name, pat in PLATFORM_RISK_RULES.items():
        matches = pat.findall(text)
        if matches:
            platform_hits[name] = matches

    # 3. 词库扫描
    cliche_hits = [w for w in lexicons["cliche"] if w in text]
    preachy_hits = [w for w in lexicons["preachy"] if w in text]
    risk_hits = [w for w in lexicons["risk"] if w in text]

    # 4. 综合评分计算
    # 基准分：硬禁项 × 15分 + 软扣分项 × 3分 + 词库项 × 2分 + 超长句 × 2分 + 平台合规项 × 30分
    score = (
        sum(len(v) for v in hard_hits.values()) * 15
        + sum(len(v) for v in soft_hits.values()) * 3
        + len(cliche_hits) * 2
        + len(preachy_hits) * 3
        + len(risk_hits) * 10
        + len(long_sents) * 2
        + sum(len(v) for v in platform_hits.values()) * 30
    )

    if score == 0:
        level = "clean"
    elif score <= 20:
        level = "轻微"
    elif score <= 60:
        level = "混合"
    else:
        level = "重度"

    return {
        "filename": filename,
        "cjk_chars": cjk_chars,
        "score": score,
        "level": level,
        "sentence_count": len(sentences),
        "sentence_cv": round(sent_cv, 2),
        "paragraph_count": len(paras),
        "paragraph_cv": round(para_cv, 2),
        "long_sentences_count": len(long_sents),
        "long_sentences_samples": [s[:35] + "..." for s in long_sents[:3]],
        "hard_hits": {k: len(v) for k, v in hard_hits.items()},
        "soft_hits": {k: len(v) for k, v in soft_hits.items()},
        "platform_hits": {k: len(v) for k, v in platform_hits.items()},
        "cliche_hits": cliche_hits,
        "preachy_hits": preachy_hits,
        "risk_hits": risk_hits,
        "passed": (score <= 20 and len(hard_hits) == 0 and len(platform_hits) == 0)
    }

def main():
    parser = argparse.ArgumentParser(description="番茄小说多维审校体检工具")
    parser.add_argument("paths", nargs="+", help="文件或目录路径")
    parser.add_argument("--clean", action="store_true", help="严格要求 clean(0) 且零硬禁，否则返回非零退出码")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    files = []
    for p in args.paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.glob("**/*.md")))
            files.extend(sorted(path.glob("**/*.txt")))

    if not files:
        print("未找到需要检查的文件。")
        sys.exit(1)

    lexicons = get_default_lexicons()
    results = []
    all_clean = True

    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"读取文件失败 {f}: {e}", file=sys.stderr)
            continue
        res = audit_text(content, filename=f.name, lexicons=lexicons)
        results.append(res)
        if args.clean and not (res["score"] == 0 and len(res["hard_hits"]) == 0 and len(res["platform_hits"]) == 0):
            all_clean = False

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"=== {r['filename']} (字数={r['cjk_chars']}) ===")
            print(f"档位: {r['level']} ({r['score']}) | 硬禁项: {sum(r['hard_hits'].values())} | 平台风险: {sum(r['platform_hits'].values())}")
            print(f"句数: {r['sentence_count']} (CV={r['sentence_cv']}) | 段数: {r['paragraph_count']} (CV={r['paragraph_cv']}) | 超长句(>45字): {r['long_sentences_count']}")
            if r["hard_hits"]:
                print(f"  [硬禁命中] {r['hard_hits']}")
            if r["soft_hits"]:
                print(f"  [软扣分命中] {r['soft_hits']}")
            if r["platform_hits"]:
                print(f"  [平台风险] {r['platform_hits']}")
            if r["cliche_hits"]:
                print(f"  [套话命中] {r['cliche_hits']}")
            if r["preachy_hits"]:
                print(f"  [说教命中] {r['preachy_hits']}")
            if r["risk_hits"]:
                print(f"  [合规风险] {r['risk_hits']}")
            if r["long_sentences_samples"]:
                print(f"  [超长句样本] {r['long_sentences_samples']}")
            print()

    if args.clean and not all_clean:
        sys.exit(1)

if __name__ == "__main__":
    main()
