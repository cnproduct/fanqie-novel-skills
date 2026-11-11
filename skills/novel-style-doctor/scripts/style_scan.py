#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""网文文风诊断扫描器 —— 基于公开 AI 检测原理的本地代理分析。

用法:
    python style_scan.py <文件路径> [--json 输出.json] [--no-paragraph]

说明:
    本地无法真正运行大模型计算困惑度(Perplexity)，因此本脚本用一组
    "代理指标" 逼近主流平台(AIGC检测)与番茄低质治理的判定逻辑，
    加权合成一个 0-1 的 AIGC 特征值。

    本脚本基于公开的 AI 文本检测原理(困惑度 + 爆发度 + 统计指纹)，
    并参考网文平台的公开低质治理规则(如番茄《低质内容治理公告》的
    "空洞水文""结构失常"两类)搭建。结果仅供作者自检文风参考。

维度与主流 AI 检测/平台口径的对应:
    1. 困惑度代理  <- 困惑度(Perplexity)：高频虚词、逻辑连接词、bigram 重复
    2. 爆发度      <- 爆发性(Burstiness)：句长/段长/章字数 CV、句长标准差
    3. 统计指纹    <- 词频异常/叙事指纹：黑名单词、高频副词、标点指纹
    4. 句式模板    <- 句式单一/叙事逻辑工整：时间锚点、不是…而是…、段首重复
    5. 情感扁平度  <- 情绪波动平缓：情绪标签词、心理描写标记词
    6. 低质水文    <- 番茄"空洞水文/结构失常"：对话占比(反向)、流水账连接词、
                      高级概念词、具体性密度(数字+地名+专名，反向)

输出口径(对标主流检测 AIGC 值 0-1):
    < 0.40        人工特征(安全)
    0.40 - 0.55   偏人工(可投，注意个别片段)
    0.55 - 0.70   疑似 AI(建议改写)
    0.70 - 0.85   高度疑似 AI(必须改写)
    >= 0.85       AI 特征(大概率机器生成)

    主流 AI 检测的三段口径: 0-0.5 人工 / 0.5-0.99 疑似AI / 0.99-1 AI 特征。
    本脚本在此基础上细分五档，便于投稿决策。

注意: 结果仅供自检参考，不能作为平台判定的唯一依据。真实平台还有
      人工复审与读者举报，且检测模型持续更新。
"""
import sys
import re
import json
import math
from collections import Counter
from pathlib import Path

# ============================================================
# 词表（阈值口径见 references/scoring-rubric.md 第三节）
# ============================================================

# 1. 高频虚词（困惑度代理：AI 过度规范使用这些字）
FUNCTION_CHARS = "的了是在着就都和也还一不又很更"

# 2. 逻辑连接词（困惑度 + 语义连贯性代理：AI 过渡"丝滑"）
CONNECTIVES = [
    "但是", "然而", "因此", "所以", "此外", "同时", "于是", "然后",
    "接着", "随后", "不过", "况且", "总之", "总而言之", "由此可见",
    "显而易见", "换句话说", "与此同时", "就这样",
]

# 3. AI 味黑名单词（统计指纹：高频锚点词）
BLACKLIST = [
    "宛如", "仿佛", "交织", "弥漫", "充斥着", "深邃", "熠熠", "袅袅",
    "缓缓", "微微", "不禁", "暗自", "眸光", "周身", "气息", "悄然",
    "蓦地", "骤然", "映入眼帘", "愈发", "周遭", "瞳孔骤缩", "冷哼一声",
    "心头一紧", "倒吸一口凉气", "心中掀起惊涛骇浪", "不可思议",
    "一股怒火涌上心头", "感到一阵绝望", "复杂的情绪", "就在这时",
    "与此同时", "殊不知", "刹那间", "下一秒", "此时此刻",
    "空气仿佛凝固", "时间仿佛静止", "命运的齿轮",
    "嘴角勾起", "眼中闪过一丝", "不由得", "下意识地", "沉默了几秒",
    "顿了一下", "看了他一眼", "没有说话",
    "瞳孔地震", "一股无形的压迫感", "只见",
    "眼神干净", "声音沉稳", "不疾不徐", "面不改色", "冷静果断",
    "临危不乱", "游刃有余", "泰然自若", "举重若轻",
    "今天就是你的死期", "你成功激怒我了", "不知天高地厚",
    "让你见识真正的力量", "这就是你的遗言了",
    "脸色大变", "眉宇微蹙", "周身萦绕", "宛如实质", "缓缓抬手", "微微侧头",
    "嘴角勾起一抹弧度",
]

# 4. 高频程度副词（统计指纹：AI 副词过度集中）
ADVERBS = [
    "极其", "异常", "不可思议", "愈发", "骤然", "蓦地", "格外", "颇为",
    "颇为", "相当", "极为", "十分", "莫名", "莫名地", "无端", "竟然",
]

# 5. 时间锚点词（句式模板：AI 滥用时间转折）
TIME_ANCHORS = [
    "就在这时", "与此同时", "殊不知", "刹那间", "下一秒", "此时此刻",
    "此刻", "正当此时", "突然", "忽然", "猛地", "骤然间", "电光火石",
]

# 6. 心理描写标记词（情感扁平度：AI 用心理标签替代生理反应）
PSYCH_MARKERS = [
    "心想", "暗道", "心中", "内心", "不禁", "暗自", "心头", "内心深处",
    "心里", "思绪", "心绪", "心头一紧", "心下一沉", "下意识地",
]

# 7. 情绪标签词（情感扁平度：AI 直接贴情绪标签而非描写）
EMOTION_LABELS = [
    "愤怒", "恐惧", "悲伤", "喜悦", "惊讶", "绝望", "兴奋", "激动",
    "焦虑", "不安", "感动", "心疼", "难过", "高兴", "失落", "紧张",
    "悲愤", "狂喜", "悲痛", "惊恐", "欣慰", "愧疚", "懊悔",
]

# 8. 口语/惊奇词（反向指标：人类独有，AI 少见）
COLLOQUIALS = [
    "卧槽", "靠", "妈的", "他妈的", "我靠", "牛逼", "麻了", "离谱",
    "蚌埠", "笑死", "破防", "上头", "绝了", "这波", "属实", "搁",
    "咋", "啥", "嘞", "呗", "嘛", "甭", "贼", "得嘞", "好家伙",
]

# 9. 流水账连接词（低质水文：机械罗列时间/动作/对话的"流水账式叙事"）
FLOW_CONNECTIVES = [
    "然后", "接着", "随后", "于是", "紧接着", "再然后", "之后",
    "接下来", "过后", "旋即",
]

# 10. 高级抽象概念词（低质水文：堆砌艰涩难懂高级概念，无可读性）
ABSTRACT_WORDS = [
    "本质上", "底层逻辑", "赋能", "闭环", "维度", "核心", "关键",
    "深刻", "境界", "领域", "层面", "意义", "价值", "所谓", "格局",
    "认知", "体系", "框架", "逻辑", "赛道", "路径", "范式", "矩阵",
]

# 11. 具体性正则（低质水文反向指标：具体数字/地名/专名，AI"行文空泛"偏泛化）
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
PLACE_RE = re.compile(r"[\u4e00-\u9fa5]{1,6}(?:县|市|区|镇|村|街|路|巷|号|院|楼|小区|大厦|广场|公园|车站|机场)")
PROPER_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,15}|《[^》]{1,20}》|「[^」]{1,20}」")

CHAPTER_RE = re.compile(r"^\s*(第[0-9零一二三四五六七八九十百千]+[章节回]|Chapter\s+\d+)", re.IGNORECASE)


# ============================================================
# 基础工具
# ============================================================

def read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"错误: 文件不存在 {path}", file=sys.stderr)
        sys.exit(1)
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    print("错误: 无法识别文件编码 (尝试过 utf-8/gbk)", file=sys.stderr)
    sys.exit(1)


def split_chapters(text: str):
    """按章节标题切分; 无标题则整体为一章。"""
    lines = text.splitlines()
    chapters, cur_title, cur_lines = [], "全文", []
    for line in lines:
        if CHAPTER_RE.match(line) and len(line.strip()) < 40:
            if cur_lines and any(l.strip() for l in cur_lines):
                chapters.append((cur_title, "\n".join(cur_lines)))
            cur_title, cur_lines = line.strip(), []
        else:
            cur_lines.append(line)
    if cur_lines and any(l.strip() for l in cur_lines):
        chapters.append((cur_title, "\n".join(cur_lines)))
    return chapters or [("全文", text)]


def split_sentences(body: str):
    parts = re.split(r"[。！？!?…\n]+", body)
    return [p.strip() for p in parts if p.strip()]


def cv(values):
    """变异系数 = 标准差 / 均值。"""
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var) / mean


def stdev(values):
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var)


def strip_ws(s: str) -> str:
    return re.sub(r"\s", "", s)


def chars(s: str) -> list:
    """返回中文字符列表（用于 n-gram）。"""
    return re.findall(r"[\u4e00-\u9fa5]", s)


# ============================================================
# 归一化：把原始值映射到 0-1 的 "AI 特征值"（0=像人, 1=像AI）
# ============================================================

def norm_high(value, ai_thresh, human_thresh):
    """值越大越像 AI。>=ai_thresh 记 1, <=human_thresh 记 0。"""
    if value >= ai_thresh:
        return 1.0
    if value <= human_thresh:
        return 0.0
    return (value - human_thresh) / (ai_thresh - human_thresh)


def norm_low(value, human_thresh, ai_thresh):
    """值越小越像 AI。<=ai_thresh 记 1, >=human_thresh 记 0。"""
    if value <= ai_thresh:
        return 1.0
    if value >= human_thresh:
        return 0.0
    return (human_thresh - value) / (human_thresh - ai_thresh)


def clamp01(x):
    return max(0.0, min(1.0, x))


# ============================================================
# 各维度计算
# ============================================================

def metric(func_word_density, connective_density, bigram_repeat):
    """困惑度代理维度。"""
    # 高频虚词密度（每千字）
    m1 = norm_high(func_word_density, 260, 170)          # AI 虚词更密集
    # 逻辑连接词密度（每千字）
    m2 = norm_high(connective_density, 8.0, 3.0)          # AI 连接词更密
    # bigram 重复率（0-1）
    m3 = norm_high(bigram_repeat, 0.45, 0.25)             # AI 重复搭配更多
    return m1, m2, m3


def compute_perplexity_proxies(all_chars, total_chars, text):
    """计算困惑度代理的四个原始指标。"""
    # 高频虚词密度
    func_count = sum(text.count(c) for c in FUNCTION_CHARS)
    func_density = func_count / max(total_chars, 1) * 1000

    # 逻辑连接词密度
    connective_count = sum(text.count(w) for w in CONNECTIVES)
    connective_density = connective_count / max(total_chars, 1) * 1000

    # bigram 重复率
    bigrams = [all_chars[i] + all_chars[i + 1] for i in range(len(all_chars) - 1)]
    if bigrams:
        bc = Counter(bigrams)
        repeated = sum(1 for v in bc.values() if v >= 2)
        bigram_repeat = repeated / len(set(bigrams))
    else:
        bigram_repeat = 0.0

    return func_density, connective_density, bigram_repeat


def compute_burstiness(sent_lens, para_lens, chapter_words):
    """爆发度维度。"""
    s_cv = cv(sent_lens)
    p_cv = cv(para_lens)
    c_cv = cv(chapter_words) if len(chapter_words) > 1 else 0.0

    m_sent = norm_low(s_cv, 0.55, 0.30)                   # 句长 CV 低 -> AI
    m_para = norm_low(p_cv, 0.65, 0.40)                   # 段长 CV 低 -> AI
    m_chap = norm_low(c_cv, 0.20, 0.10)                   # 章字数 CV 低 -> AI

    # 句长标准差（AI 5-8，人类 >8）
    sd = stdev(sent_lens)
    m_sd = norm_low(sd, 9.0, 6.5)

    # 短句/长句占比失衡
    short_ratio = sum(1 for l in sent_lens if l <= 10) / max(len(sent_lens), 1)
    long_ratio = sum(1 for l in sent_lens if l >= 40) / max(len(sent_lens), 1)

    return {
        "句长CV": (s_cv, m_sent),
        "句长标准差": (sd, m_sd),
        "段长CV": (p_cv, m_para),
        "章字数CV": (c_cv, m_chap),
        "短句占比(<=10字)": short_ratio,
        "长句占比(>=40字)": long_ratio,
    }


def compute_fingerprint(text, total_chars):
    """统计指纹维度。"""
    k10 = max(total_chars, 1) / 1000

    # 黑名单词频（每万字）
    black_hits = Counter()
    for w in BLACKLIST:
        n = text.count(w)
        if n:
            black_hits[w] = n
    black_total = sum(black_hits.values())
    black_per10k = black_total / max(total_chars, 1) * 10000
    m_black = norm_high(black_per10k, 25, 8)

    # 高频副词密度
    adv_total = sum(text.count(w) for w in ADVERBS)
    adv_per10k = adv_total / max(total_chars, 1) * 10000
    m_adv = norm_high(adv_per10k, 20, 6)

    # 标点指纹
    dash_per_k = text.count("——") / k10
    ellip_per_k = (text.count("……") + text.count("...")) / k10
    excl_per_k = text.count("！") / k10
    # 破折号：0.5-2.0 正常；过高是 AI 典型特征，完全不用只是弱信号
    if dash_per_k >= 1.0:
        m_dash = norm_high(dash_per_k, 2.5, 1.8)
    elif dash_per_k <= 0.05:
        m_dash = 0.4
    else:
        m_dash = norm_low(dash_per_k, 0.5, 0.2)
    # 省略号：>6 或 =0 为弱异常信号（很多人工文本也不用省略号）
    if ellip_per_k <= 0.1:
        m_ellip = 0.5
    elif ellip_per_k >= 6:
        m_ellip = 0.8
    else:
        m_ellip = 0.0

    return {
        "黑名单词频(每万字)": (black_per10k, m_black, black_hits.most_common(10)),
        "高频副词(每万字)": (adv_per10k, m_adv, None),
        "破折号(每千字)": (dash_per_k, m_dash, None),
        "省略号(每千字)": (ellip_per_k, m_ellip, None),
        "感叹号(每千字)": (excl_per_k, 0.0, None),
    }


def classify_start(paragraph: str) -> str:
    p = paragraph.strip()
    if not p:
        return ""
    if p.startswith(("“", "「", '"')):
        return "对话开头"
    if re.match(r"^(他|她|它)[^，。]", p):
        return "他/她+动作"
    if p.startswith(("随着", "当", "对于", "就在", "与此同时", "此时", "此刻", "突然", "忽然")):
        return "介词/时间开头"
    if re.match(r"^\d", p):
        return "数字开头"
    if re.match(r"^[\u4e00-\u9fa5]{1,3}(说道|问道|喊道|笑道|说|道|问|喊|叫|笑)(了|着|：|:|\"|「|“)", p):
        return "人名+说"
    return "其他"


def compute_patterns(chapters):
    """句式模板维度。"""
    full = "\n".join(b for _, b in chapters)
    total = len(strip_ws(full))

    # 不是…而是…
    not_but = len(re.findall(r"不是[^。！？!?]{1,20}而是", full))
    m_notbut = norm_high(not_but / max(total, 1) * 10000, 4, 1)

    # 时间锚点词密度
    time_count = sum(full.count(w) for w in TIME_ANCHORS)
    m_time = norm_high(time_count / max(total, 1) * 10000, 15, 5)

    # 段首模式（模板化段首占比）
    start_counter = Counter()
    total_paras = 0
    for _, body in chapters:
        for p in body.split("\n"):
            cls = classify_start(p)
            if not cls:
                continue
            start_counter[cls] += 1
            total_paras += 1
    suspicious = {k: v for k, v in start_counter.items() if k != "其他"}
    top_ratio = 0.0
    if suspicious and total_paras:
        top_ratio = max(suspicious.values()) / total_paras
    m_start = norm_high(top_ratio, 0.35, 0.18)

    return {
        "不是…而是…(每万字)": (not_but / max(total, 1) * 10000, m_notbut, None),
        "时间锚点词(每万字)": (time_count / max(total, 1) * 10000, m_time, None),
        "模板化段首占比": (top_ratio, m_start, dict(start_counter)),
    }


def compute_emotion(text, total_chars):
    """情感扁平度维度。"""
    # 情绪标签词密度
    emo_count = sum(text.count(w) for w in EMOTION_LABELS)
    emo_density = emo_count / max(total_chars, 1) * 10000
    # 情绪标签过多 -> 贴标签而非描写 -> AI；过少 -> 可能无情绪波动
    if emo_density >= 25:
        m_emo = 1.0
    elif emo_density <= 2:
        m_emo = 0.6
    else:
        m_emo = norm_high(emo_density, 25, 8)

    # 心理描写标记词密度
    psy_count = sum(text.count(w) for w in PSYCH_MARKERS)
    psy_density = psy_count / max(total_chars, 1) * 10000
    m_psy = norm_high(psy_density, 30, 10)

    # 口语/惊奇词（反向）
    collo_count = sum(text.count(w) for w in COLLOQUIALS)
    collo_density = collo_count / max(total_chars, 1) * 10000
    m_collo = norm_low(collo_density, 8, 2)  # 口语词少 -> AI

    return {
        "情绪标签词(每万字)": (emo_density, m_emo, None),
        "心理标记词(每万字)": (psy_density, m_psy, None),
        "口语词(每万字)": (collo_density, m_collo, None),
    }


def compute_lowquality(text, total_chars):
    """低质水文维度（番茄官方"空洞水文/结构失常"）。
    - 对话占比：反向指标。流水账/梗概式写文缺对话，AI 水文尤甚。
    - 流水账连接词：高→AI（机械罗列时间/动作/对话）。
    - 高级概念词：高→AI（堆砌艰涩难懂高级概念，无可读性）。
    - 具体性密度：反向指标（数字+地名+专名）。"行文空泛"=缺具体细节，AI 偏好泛化。
    """
    # 对话占比（引号内字数 / 全文）
    dialogue_chars = 0
    for m in re.finditer(r"[“\"「『]([^”\"」』]*)[”\"」』]", text):
        dialogue_chars += len(strip_ws(m.group(1)))
    dialogue_ratio = dialogue_chars / max(total_chars, 1)
    m_dialogue = norm_low(dialogue_ratio, 0.35, 0.12)   # 对话占比 <12% 偏 AI

    # 流水账连接词密度（每万字）
    flow_count = sum(text.count(w) for w in FLOW_CONNECTIVES)
    flow_density = flow_count / max(total_chars, 1) * 10000
    m_flow = norm_high(flow_density, 30, 12)

    # 高级抽象概念词密度（每万字）
    abstract_count = sum(text.count(w) for w in ABSTRACT_WORDS)
    abstract_density = abstract_count / max(total_chars, 1) * 10000
    m_abstract = norm_high(abstract_density, 25, 8)

    # 具体性密度（数字 + 地名 + 专名，每万字；反向：越低越"空泛"）
    num_count = len(NUMBER_RE.findall(text))
    place_count = len(PLACE_RE.findall(text))
    proper_count = len(PROPER_RE.findall(text))
    spec_density = (num_count + place_count + proper_count) / max(total_chars, 1) * 10000
    m_spec = norm_low(spec_density, 45, 15)

    return {
        "对话占比": (dialogue_ratio, m_dialogue, None),
        "流水账连接词(每万字)": (flow_density, m_flow, None),
        "高级概念词(每万字)": (abstract_density, m_abstract, None),
        "具体性密度(数字+地名+专名/每万字)": (spec_density, m_spec, None),
    }


# ============================================================
# 综合评分
# ============================================================

def overall_score(dims):
    """加权合成 0-1 AIGC 特征值。权重对标主流检测'困惑度+爆发度'为核心。"""
    weights = {
        "困惑度代理": 0.20,
        "爆发度": 0.30,
        "统计指纹": 0.15,
        "句式模板": 0.12,
        "情感扁平度": 0.08,
        "低质水文": 0.15,
    }
    score = sum(dims[k]["score"] * weights[k] for k in weights)
    return score, weights


def risk_level(score):
    if score < 0.40:
        return "人工特征(安全)", "🟢"
    if score < 0.55:
        return "偏人工(可投，注意个别片段)", "🟡"
    if score < 0.70:
        return "疑似AI(建议改写)", "🟠"
    if score < 0.85:
        return "高度疑似AI(必须改写)", "🔴"
    return "AI特征(大概率机器生成)", "⛔"


# ============================================================
# 扫描主流程
# ============================================================

def scan(text: str):
    chapters = split_chapters(text)
    full = "\n".join(b for _, b in chapters)
    total_chars = len(strip_ws(full))
    all_chars = chars(full)

    report = {
        "总字数(去空白)": total_chars,
        "章节数": len(chapters),
        "维度": {},
        "每章明细": [],
    }

    # 1. 困惑度代理
    fd, cd, br = compute_perplexity_proxies(all_chars, total_chars, full)
    p1, p2, p3 = metric(fd, cd, br)
    report["维度"]["困惑度代理"] = {
        "score": (p1 * 0.40 + p2 * 0.35 + p3 * 0.25),
        "指标": {
            "高频虚词密度(每千字)": (fd, p1, "AI 更密集"),
            "逻辑连接词(每千字)": (cd, p2, "AI 过渡更丝滑"),
            "bigram重复率": (br, p3, "AI 固定搭配更多"),
        },
    }

    # 2. 爆发度
    all_sent_lens, all_para_lens, chapter_words = [], [], []
    for _, body in chapters:
        sents = split_sentences(body)
        sent_lens = [len(strip_ws(s)) for s in sents]
        paras = [strip_ws(p) for p in body.split("\n") if p.strip()]
        para_lens = [len(p) for p in paras]
        all_sent_lens += sent_lens
        all_para_lens += para_lens
        chapter_words.append(len(strip_ws(body)))
    burst = compute_burstiness(all_sent_lens, all_para_lens, chapter_words)
    b_metrics = {}
    b_score = 0.0
    for k, v in burst.items():
        if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], float):
            b_metrics[k] = v
    b_score = (
        burst["句长CV"][1] * 0.35
        + burst["句长标准差"][1] * 0.15
        + burst["段长CV"][1] * 0.25
        + burst["章字数CV"][1] * 0.25
    )
    report["维度"]["爆发度"] = {"score": b_score, "指标": b_metrics}

    # 3. 统计指纹
    fp = compute_fingerprint(full, total_chars)
    report["黑名单TOP"] = fp["黑名单词频(每万字)"][2]
    f_metrics = {k: (v[0], v[1]) for k, v in fp.items()}
    f_score = (
        fp["黑名单词频(每万字)"][1] * 0.40
        + fp["高频副词(每万字)"][1] * 0.25
        + fp["破折号(每千字)"][1] * 0.20
        + fp["省略号(每千字)"][1] * 0.15
    )
    report["维度"]["统计指纹"] = {"score": f_score, "指标": f_metrics}

    # 4. 句式模板
    pat = compute_patterns(chapters)
    p_metrics = {k: (v[0], v[1]) for k, v in pat.items()}
    p_score = (
        pat["不是…而是…(每万字)"][1] * 0.30
        + pat["时间锚点词(每万字)"][1] * 0.35
        + pat["模板化段首占比"][1] * 0.35
    )
    report["维度"]["句式模板"] = {"score": p_score, "指标": p_metrics}

    # 5. 情感扁平度
    emo = compute_emotion(full, total_chars)
    e_metrics = {k: (v[0], v[1]) for k, v in emo.items()}
    e_score = (
        emo["情绪标签词(每万字)"][1] * 0.35
        + emo["心理标记词(每万字)"][1] * 0.35
        + emo["口语词(每万字)"][1] * 0.30
    )
    report["维度"]["情感扁平度"] = {"score": e_score, "指标": e_metrics}

    # 6. 低质水文
    lowq = compute_lowquality(full, total_chars)
    l_metrics = {k: (v[0], v[1]) for k, v in lowq.items()}
    l_score = (
        lowq["对话占比"][1] * 0.30
        + lowq["流水账连接词(每万字)"][1] * 0.25
        + lowq["高级概念词(每万字)"][1] * 0.20
        + lowq["具体性密度(数字+地名+专名/每万字)"][1] * 0.25
    )
    report["维度"]["低质水文"] = {"score": l_score, "指标": l_metrics}

    # 综合
    total_score, weights = overall_score(report["维度"])
    # 匀速填字硬托底：章节数足够时，章字数高度均匀是 AI 匀速填字的铁证。
    # 即使词句层面已洗掉 AI 味锚点词、其他维度全绿，节奏匀速也会暴露机器生成。
    # 兑现 scoring-rubric.md "章字数 CV 是最硬的一条" 的承诺。
    if len(chapter_words) >= 3:
        chap_cv = burst["章字数CV"][0]
        if chap_cv <= 0.06:
            total_score = max(total_score, 0.70)
        elif chap_cv <= 0.10:
            total_score = max(total_score, 0.55)
    report["AIGC特征值"] = round(total_score, 3)
    level, icon = risk_level(total_score)
    report["风险等级"] = level
    report["风险图标"] = icon

    # 逐章明细（对每章单独跑核心指标）
    for title, body in chapters:
        c_chars = len(strip_ws(body))
        c_sents = [len(strip_ws(s)) for s in split_sentences(body)]
        c_paras = [len(strip_ws(p)) for p in body.split("\n") if p.strip()]
        c_sent_cv = cv(c_sents)
        # 该章黑名单密度
        c_black = sum(body.count(w) for w in BLACKLIST) / max(c_chars, 1) * 10000
        report["每章明细"].append({
            "章节": title[:24],
            "字数": c_chars,
            "句长CV": round(c_sent_cv, 3),
            "段落CV": round(cv(c_paras), 3),
            "黑名单密度(每万字)": round(c_black, 1),
        })

    # 高密度锚点段落（命中黑名单词/时间锚点/心理标记的段落）
    report["高密度段落"] = find_dense_paragraphs(chapters)

    return report


def find_dense_paragraphs(chapters, top_n=8):
    """找出命中锚点词最多的段落（用于逐段定位）。"""
    hits = []
    for _, body in chapters:
        for p in body.split("\n"):
            p = p.strip()
            if not p:
                continue
            score = 0
            for w in BLACKLIST:
                if w in p:
                    score += 1
            for w in TIME_ANCHORS:
                if w in p:
                    score += 1
            for w in PSYCH_MARKERS:
                if w in p:
                    score += 1
            if score >= 2:
                hits.append((score, p[:60]))
    hits.sort(key=lambda x: -x[0])
    return hits[:top_n]


# ============================================================
# 输出
# ============================================================

def print_report(report):
    w = 60
    print("=" * w)
    print("网文文风诊断报告（本地代理）")
    print("=" * w)
    score = report["AIGC特征值"]
    icon = report["风险图标"]
    print(f"\n总字数: {report['总字数(去空白)']}  |  章节数: {report['章节数']}")
    print(f"\n>>> AIGC 特征值: {score:.3f}  {icon} {report['风险等级']}")

    print("\n" + "-" * w)
    print("各维度得分（0=像人，1=像AI）")
    print("-" * w)
    for dim, data in report["维度"].items():
        bar = "█" * int(data["score"] * 20)
        print(f"  {dim:<8} {data['score']:.3f}  {bar}")

    for dim, data in report["维度"].items():
        print(f"\n【{dim}】")
        for k, v in data["指标"].items():
            raw = v[0]
            s = v[1]
            if isinstance(raw, float):
                print(f"  {k:<20} 原始={raw:.2f}  AI分={s:.2f}")
            else:
                print(f"  {k:<20} 原始={raw}  AI分={s:.2f}")

    # 黑名单 TOP
    if report.get("黑名单TOP"):
        print("\n【黑名单高频词】")
        for w, n in report["黑名单TOP"]:
            print(f"  {w} × {n}")
    else:
        print("\n【黑名单高频词】无（未命中 AI 味锚点词）")

    print("\n【每章明细】")
    for c in report["每章明细"]:
        print(f"  {c['章节']:<24} {c['字数']}字  句长CV={c['句长CV']}  段落CV={c['段落CV']}  黑名单密度={c['黑名单密度(每万字)']}")

    if "高密度段落" in report and report["高密度段落"]:
        print("\n【高密度锚点段落（建议优先改写）】")
        for s, txt in report["高密度段落"]:
            print(f"  [{s}命中] {txt}...")
    else:
        print("\n【高密度锚点段落】无（未发现明显聚集）")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    text = read_text(sys.argv[1])
    report = scan(text)

    json_path = None
    if "--json" in sys.argv:
        idx = sys.argv.index("--json")
        json_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "style_report.json"
        Path(json_path).write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print_report(report)

    if json_path:
        print(f"\nJSON 报告已保存: {json_path}")


if __name__ == "__main__":
    main()
