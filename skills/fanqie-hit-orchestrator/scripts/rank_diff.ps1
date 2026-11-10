<#
.SYNOPSIS
  番茄榜单快照工具：生成 CSV 模板、对比两期快照、统计标签热度。
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File rank_diff.ps1 -Mode template -Out 2026-11-10_男频新书榜.csv
  powershell -ExecutionPolicy Bypass -File rank_diff.ps1 -Mode diff -Old 旧.csv -New 新.csv -Out 变化.md
  powershell -ExecutionPolicy Bypass -File rank_diff.ps1 -Mode tags -New a.csv,b.csv -Out 标签热度.md
.NOTES
  CSV 字段：date,list,rank,title,author,tags,reads,words,status（UTF-8）。tags 用 / 分隔。
  数据只来自公开页面人工记录、作者后台或用户提供。
#>
param(
  [ValidateSet('diff', 'tags', 'template')][string]$Mode = 'diff',
  [string]$Old = "",
  [string[]]$New = @(),
  [string]$Out = "",
  [int]$Top = 10
)
$ErrorActionPreference = 'Stop'
# 通过 -File 调用时，逗号分隔的多个文件会作为一个字符串传入，这里统一拆分
$New = @($New | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

function ConvertTo-Num([string]$s) {
  if (-not $s) { return $null }
  $m = [regex]::Match($s.Trim(), '^([\d\.]+)\s*(万|亿|w|W|k|K)?')
  if (-not $m.Success) { return $null }
  $v = [double]$m.Groups[1].Value
  switch ($m.Groups[2].Value) { '万' { $v *= 1e4 } 'w' { $v *= 1e4 } 'W' { $v *= 1e4 } '亿' { $v *= 1e8 } 'k' { $v *= 1e3 } 'K' { $v *= 1e3 } }
  return $v
}
function Format-Num($v) { if ($null -eq $v) { '—' } elseif ([math]::Abs($v) -ge 1e4) { '{0:N1}万' -f ($v / 1e4) } else { '{0:N0}' -f $v } }
function Import-Snap([string]$p) {
  if (-not (Test-Path $p)) { throw "找不到快照: $p" }
  return @(Import-Csv -Path $p -Encoding UTF8 | Where-Object { $_.title -and $_.rank })
}
function Write-Report($lines) {
  $report = $lines -join "`r`n"
  if ($Out) {
    $dir = Split-Path -Parent $Out
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    [IO.File]::WriteAllText($Out, $report, (New-Object Text.UTF8Encoding $false))
    Write-Output "已写入: $Out"
  } else { Write-Output $report }
}

$o = New-Object System.Collections.Generic.List[string]

switch ($Mode) {
  'template' {
    if (-not $Out) { throw "template 模式需要 -Out" }
    $today = Get-Date -Format 'yyyy-MM-dd'
    $csv = "date,list,rank,title,author,tags,reads,words,status`r`n$today,示例榜单,1,示例书名,示例作者,重生/复仇/豪门,12.3万,56万,连载"
    $dir = Split-Path -Parent $Out
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    [IO.File]::WriteAllText($Out, $csv, (New-Object Text.UTF8Encoding $true))
    Write-Output "模板已生成: $Out（请删除示例行后填写）"
    return
  }

  'diff' {
    if (-not $Old -or $New.Count -lt 1) { throw "diff 模式需要 -Old 和 -New" }
    $a = Import-Snap $Old; $b = Import-Snap $New[0]
    $ka = @{}; foreach ($r in $a) { $ka["$($r.list)||$($r.title)"] = $r }
    $kb = @{}; foreach ($r in $b) { $kb["$($r.list)||$($r.title)"] = $r }

    $added = @($b | Where-Object { -not $ka.ContainsKey("$($_.list)||$($_.title)") } | Sort-Object { [int]$_.rank })
    $dropped = @($a | Where-Object { -not $kb.ContainsKey("$($_.list)||$($_.title)") } | Sort-Object { [int]$_.rank })
    $both = foreach ($r in $b) {
      $k = "$($r.list)||$($r.title)"
      if ($ka.ContainsKey($k)) {
        $p = $ka[$k]
        $ra = ConvertTo-Num $p.reads; $rb = ConvertTo-Num $r.reads
        [pscustomobject]@{
          List = $r.list; Title = $r.title; Tags = $r.tags
          OldRank = [int]$p.rank; NewRank = [int]$r.rank; Delta = [int]$p.rank - [int]$r.rank
          ReadsGrowth = if ($null -ne $ra -and $null -ne $rb) { $rb - $ra } else { $null }
        }
      }
    }
    $both = @($both)

    $o.Add("# 榜单变化：$([IO.Path]::GetFileName($Old)) → $([IO.Path]::GetFileName($New[0]))")
    $o.Add("")
    $o.Add("- 旧快照 $($a.Count) 条，新快照 $($b.Count) 条；新上榜 $($added.Count)，跌出 $($dropped.Count)，持续在榜 $($both.Count)")
    $o.Add("")
    $o.Add("## 一、新上榜（黑马候选）")
    $o.Add(""); $o.Add("| 榜单 | 排名 | 书名 | 标签 | 阅读 |"); $o.Add("| :--- | :- | :--- | :--- | :- |")
    foreach ($r in $added) { $o.Add("| $($r.list) | $($r.rank) | $($r.title) | $($r.tags) | $($r.reads) |") }
    $o.Add("")
    $o.Add("## 二、排名跃升 Top $Top")
    $o.Add(""); $o.Add("| 榜单 | 书名 | 旧→新 | 变化 | 标签 |"); $o.Add("| :--- | :--- | :- | :- | :--- |")
    foreach ($r in ($both | Where-Object { $_.Delta -gt 0 } | Sort-Object Delta -Descending | Select-Object -First $Top)) {
      $o.Add("| $($r.List) | $($r.Title) | $($r.OldRank)→$($r.NewRank) | +$($r.Delta) | $($r.Tags) |")
    }
    $o.Add("")
    $o.Add("## 三、排名下滑 Top $Top")
    $o.Add(""); $o.Add("| 榜单 | 书名 | 旧→新 | 变化 |"); $o.Add("| :--- | :--- | :- | :- |")
    foreach ($r in ($both | Where-Object { $_.Delta -lt 0 } | Sort-Object Delta | Select-Object -First $Top)) {
      $o.Add("| $($r.List) | $($r.Title) | $($r.OldRank)→$($r.NewRank) | $($r.Delta) |")
    }
    $o.Add("")
    $growth = @($both | Where-Object { $null -ne $_.ReadsGrowth } | Sort-Object ReadsGrowth -Descending | Select-Object -First $Top)
    if ($growth.Count) {
      $o.Add("## 四、阅读增长 Top $Top")
      $o.Add(""); $o.Add("| 榜单 | 书名 | 增长 | 当前排名 |"); $o.Add("| :--- | :--- | :- | :- |")
      foreach ($r in $growth) { $o.Add("| $($r.List) | $($r.Title) | $(Format-Num $r.ReadsGrowth) | $($r.NewRank) |") }
      $o.Add("")
    }
    $o.Add("## 五、跌出榜单")
    $o.Add(""); $o.Add("| 榜单 | 原排名 | 书名 | 标签 |"); $o.Add("| :--- | :- | :--- | :--- |")
    foreach ($r in $dropped) { $o.Add("| $($r.list) | $($r.rank) | $($r.title) | $($r.tags) |") }
    Write-Report $o
  }

  'tags' {
    if ($New.Count -lt 1) { throw "tags 模式需要 -New（可逗号分隔多个文件）" }
    $rows = @(); foreach ($f in $New) { $rows += Import-Snap $f }
    $maxRank = @{}
    foreach ($g in ($rows | Group-Object list)) { $maxRank[$g.Name] = ($g.Group | ForEach-Object { [int]$_.rank } | Measure-Object -Maximum).Maximum }
    $top10Rows = @($rows | Where-Object { [int]$_.rank -le 10 }).Count
    $stat = @{}
    foreach ($r in $rows) {
      if (-not $r.tags) { continue }
      $score = $maxRank[$r.list] + 1 - [int]$r.rank
      foreach ($t in ($r.tags -split '[/、;；,，|]')) {
        $t = $t.Trim(); if (-not $t) { continue }
        if (-not $stat.ContainsKey($t)) { $stat[$t] = [pscustomobject]@{ Tag = $t; Score = 0; Count = 0; Top10 = 0 } }
        $stat[$t].Score += $score; $stat[$t].Count += 1
        if ([int]$r.rank -le 10) { $stat[$t].Top10 += 1 }
      }
    }
    $o.Add("# 标签热度：$((($New | ForEach-Object { [IO.Path]::GetFileName($_) }) -join '，'))")
    $o.Add("")
    $o.Add("- 热度分 = Σ(该榜最大排名 + 1 − 排名)，排名越靠前权重越高")
    $o.Add("- Top10 占比 = 含该标签的 Top10 书数 / 全部 Top10 书数（$top10Rows）；经验上 > 40% 视为红海")
    $o.Add("")
    $o.Add("| 标签 | 热度分 | 上榜书数 | Top10 占比 | 初判 |")
    $o.Add("| :--- | :- | :- | :- | :--- |")
    foreach ($s in ($stat.Values | Sort-Object Score -Descending)) {
      $share = if ($top10Rows) { [math]::Round(100.0 * $s.Top10 / $top10Rows, 1) } else { 0 }
      $judge = if ($share -gt 40) { '红海' } elseif ($s.Top10 -eq 0 -and $s.Count -ge 2) { '腰部聚集（观察）' } elseif ($share -gt 0 -and $share -le 20) { '潜力/蓝海候选' } else { '常规' }
      $o.Add("| $($s.Tag) | $($s.Score) | $($s.Count) | $share% | $judge |")
    }
    Write-Report $o
  }
}
