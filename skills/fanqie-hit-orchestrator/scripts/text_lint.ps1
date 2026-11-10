<#
.SYNOPSIS
  番茄章节文本体检：字数、段落长度、对话占比、句长、词库命中（AI味/风险词/自定义）、章尾钩子信号。
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File text_lint.ps1 -Path 第001章.md -Out lint-001.md
  powershell -ExecutionPolicy Bypass -File text_lint.ps1 -Path 第001章.md -Lexicon ..\..\fanqie-growth-orchestrator\scripts\lexicons\preachy.txt
.NOTES
  词库格式：每行 "词" 或 "词|类别"，# 开头为注释。输出仅为提示，需结合语境人工判断。
#>
param(
  [Parameter(Mandatory = $true)][string]$Path,
  [string[]]$Lexicon = @(),
  [int]$MinChars = 2000,
  [int]$MaxChars = 3500,
  [int]$LongPara = 120,
  [string]$Out = "",
  [switch]$NoDefault
)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

function Get-CjkCount([string]$s) { return ([regex]::Matches($s, '[\u4e00-\u9fff]')).Count }

function Resolve-Lex([string]$p) {
  if (Test-Path $p) { return (Resolve-Path $p).Path }
  $alt = Join-Path $here $p
  if (Test-Path $alt) { return (Resolve-Path $alt).Path }
  throw "找不到词库文件: $p"
}

# ---------- 读取正文 ----------
$full = (Resolve-Path $Path).Path
$text = [IO.File]::ReadAllText($full, [Text.Encoding]::UTF8)
$body = ($text -split "`r?`n" | Where-Object { -not $_.TrimStart().StartsWith('#') }) -join "`n"

$total = Get-CjkCount $body
$paras = @($body -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
$paraCount = $paras.Count
$dialogue = @($paras | Where-Object { $_ -match '[“「"]' }).Count
$longParas = @($paras | Where-Object { (Get-CjkCount $_) -gt $LongPara })
$sentences = @([regex]::Split($body, '[。！？!?…]+') | Where-Object { (Get-CjkCount $_) -gt 0 })
$avgSent = if ($sentences.Count) { [math]::Round(($sentences | ForEach-Object { Get-CjkCount $_ } | Measure-Object -Sum).Sum / $sentences.Count, 1) } else { 0 }
$avgPara = if ($paraCount) { [math]::Round($total / $paraCount, 1) } else { 0 }
$dialogueRatio = if ($paraCount) { [math]::Round(100.0 * $dialogue / $paraCount, 1) } else { 0 }
$longRatio = if ($paraCount) { [math]::Round(100.0 * $longParas.Count / $paraCount, 1) } else { 0 }

# ---------- 词库 ----------
$lexFiles = @()
if (-not $NoDefault) {
  $lexFiles += (Join-Path $here 'lexicons\ai_cliche.txt')
  $lexFiles += (Join-Path $here 'lexicons\risk_words.txt')
}
foreach ($l in $Lexicon) { $lexFiles += (Resolve-Lex $l) }

$lexResults = @()
foreach ($lf in $lexFiles) {
  $label = [IO.Path]::GetFileNameWithoutExtension($lf)
  $lines = [IO.File]::ReadAllLines($lf, [Text.Encoding]::UTF8)
  $hits = @()
  foreach ($raw in $lines) {
    $line = $raw.Trim()
    if ($line -eq '' -or $line.StartsWith('#')) { continue }
    $parts = $line.Split('|')
    $word = $parts[0].Trim()
    $cat = if ($parts.Count -gt 1) { $parts[1].Trim() } else { $label }
    if ($word -eq '') { continue }
    $n = ([regex]::Matches($body, [regex]::Escape($word))).Count
    if ($n -gt 0) { $hits += [pscustomobject]@{ Word = $word; Category = $cat; Count = $n } }
  }
  $sum = ($hits | Measure-Object -Property Count -Sum).Sum
  if (-not $sum) { $sum = 0 }
  $density = if ($total) { [math]::Round(1000.0 * $sum / $total, 2) } else { 0 }
  $lexResults += [pscustomobject]@{ Label = $label; Hits = ($hits | Sort-Object Count -Descending); Sum = $sum; Density = $density }
}

# ---------- 章尾钩子 ----------
$trimmed = $body.Trim()
$tail = if ($trimmed.Length -gt 300) { $trimmed.Substring($trimmed.Length - 300) } else { $trimmed }
$closers = [char[]]@(0x201D, 0x22, 0x300D, 0x2019, 0x27, 0x20)  # 右引号、直引号、」、右单引号、空格
$lastChar = $trimmed.TrimEnd($closers)
$lastChar = if ($lastChar.Length) { $lastChar.Substring($lastChar.Length - 1) } else { '' }
$punctSignal = '？?！!…—'.Contains($lastChar)
$hookWords = @('突然','就在这时','就在此时','下一秒','竟然','没想到','是谁','怎么可能','门外','身后','电话','消息','话音未落','死寂','来了','不对','秘密','真相','等着')
$badWords = @('终于明白','从此','这一天','就这样','这就是','渐渐睡去','一夜无话','感悟','成长了','明白了一个道理')
$hookHits = @($hookWords | Where-Object { $tail.Contains($_) })
$badHits = @($badWords | Where-Object { $tail.Contains($_) })
$hookLevel = if ($punctSignal -and $hookHits.Count) { '强' } elseif ($punctSignal -or $hookHits.Count) { '中' } else { '弱/无' }

# ---------- 判定 ----------
function Flag([bool]$ok, [string]$level = 'WARN') { if ($ok) { 'OK' } else { $level } }
$fChars = Flag (($total -ge $MinChars) -and ($total -le $MaxChars))
$fDialog = Flag (($dialogueRatio -ge 20) -and ($dialogueRatio -le 70))
$fLong = Flag ($longRatio -le 20)
$fPara = Flag ($avgPara -le 60)
$fHook = Flag ($hookLevel -ne '弱/无')

# ---------- 输出 ----------
$o = New-Object System.Collections.Generic.List[string]
$o.Add("# 文本体检报告：$([IO.Path]::GetFileName($full))")
$o.Add("")
$o.Add("> 仅为提示，不是判决。词库命中需结合语境由总控/作者复核。")
$o.Add("")
$o.Add("## 一、基础指标")
$o.Add("")
$o.Add("| 指标 | 数值 | 参考范围（经验值） | 状态 |")
$o.Add("| :--- | :--- | :--- | :--- |")
$o.Add("| 汉字数 | $total | $MinChars - $MaxChars | $fChars |")
$o.Add("| 段落数 | $paraCount | — | — |")
$o.Add("| 段落平均汉字 | $avgPara | ≤ 60（手机屏约 3 行） | $fPara |")
$o.Add("| 长段落（>$LongPara 字）占比 | $longRatio% | ≤ 20% | $fLong |")
$o.Add("| 对话段落占比 | $dialogueRatio% | 20% - 70% | $fDialog |")
$o.Add("| 平均句长（汉字） | $avgSent | 网文常见 10 - 25 | — |")
$o.Add("")
$o.Add("## 二、词库命中")
$o.Add("")
foreach ($r in $lexResults) {
  $state = if ($r.Label -match 'risk') { if ($r.Sum -gt 0) { 'RED（需人工复核语境）' } else { 'OK' } } elseif ($r.Density -gt 3) { 'WARN' } else { 'OK' }
  $o.Add("### $($r.Label)：共 $($r.Sum) 次，每千字 $($r.Density) 次 —— $state")
  if ($r.Sum -gt 0) {
    $o.Add("")
    $o.Add("| 词 | 类别 | 次数 |")
    $o.Add("| :--- | :--- | :- |")
    foreach ($h in ($r.Hits | Select-Object -First 30)) { $o.Add("| $($h.Word) | $($h.Category) | $($h.Count) |") }
  }
  $o.Add("")
}
$o.Add("## 三、章尾钩子信号（最后 300 字）")
$o.Add("")
$o.Add("- 结尾标点信号：$(if ($punctSignal) { "有（$lastChar）" } else { "无（$lastChar）" })")
$o.Add("- 钩子词：$(if ($hookHits.Count) { $hookHits -join '、' } else { '无' })")
$o.Add("- 钩子强度判断：$hookLevel —— $fHook")
if ($badHits.Count) { $o.Add("- WARN 结尾疑似总结/升华：$($badHits -join '、')（番茄章尾应断在悬念上）") }
$o.Add("")
if ($longParas.Count) {
  $o.Add("## 四、需要拆分的长段落（前 5 个，截取开头）")
  $o.Add("")
  foreach ($p in ($longParas | Select-Object -First 5)) {
    $snip = if ($p.Length -gt 40) { $p.Substring(0, 40) + '……' } else { $p }
    $o.Add("- （$(Get-CjkCount $p) 字）$snip")
  }
  $o.Add("")
}

$report = $o -join "`r`n"
if ($Out) {
  $dir = Split-Path -Parent $Out
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  [IO.File]::WriteAllText($Out, $report, (New-Object Text.UTF8Encoding $false))
  Write-Output "报告已写入: $Out"
} else {
  Write-Output $report
}
