# CRF project log publisher
# 用法：在 PowerShell 中运行本脚本，把最新源文件复制到发布仓库并推送到 GitHub。

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$SourceRoot = 'D:\睿谊的WPS\Ferrariwork\CRF'
$PublishRoot = 'D:\睿谊的WPS\Ferrariwork\CRF\发布\crf-project-log'

$files = @(
  @{
    Name = 'CRF_Manifesto_科研白皮书.md'
    Source = Join-Path $SourceRoot 'CRF_Manifesto_科研白皮书.md'
  },
  @{
    Name = 'Simulation_交接卡.md'
    Source = Join-Path $SourceRoot '调研笔记\Simulation_交接卡.md'
  },
  @{
    Name = '两位教授访谈问题清单_2026-09-13.md'
    Source = Join-Path $SourceRoot '汇报材料\两位教授访谈问题清单_2026-09-13.md'
  },
  @{
    Name = '贡献台账_作者级贡献.md'
    Source = Join-Path $SourceRoot '调研笔记\贡献台账_作者级贡献.md'
  },
  @{
    Name = '方法论记录_不可见工作.md'
    Source = Join-Path $SourceRoot '调研笔记\方法论记录_不可见工作.md'
  },
  @{
    Name = '19簇命名依据_2026-09-15.md'
    Source = Join-Path $SourceRoot '调研笔记\19簇命名依据_2026-09-15.md'
  }
)

if (-not (Test-Path -LiteralPath $PublishRoot)) {
  New-Item -ItemType Directory -Force -Path $PublishRoot | Out-Null
}

foreach ($f in $files) {
  if (-not (Test-Path -LiteralPath $f.Source)) {
    throw "Missing source file: $($f.Source)"
  }
  $destFile = Join-Path $PublishRoot $f.Name
  Copy-Item -LiteralPath $f.Source -Destination $destFile -Force
  Write-Host "Copied $($f.Name)"
}

if (-not (Test-Path -LiteralPath (Join-Path $PublishRoot '.git'))) {
  git -C $PublishRoot init
  git -C $PublishRoot branch -M main
}

git -C $PublishRoot add -A
$changes = git -C $PublishRoot status --porcelain

if ($changes) {
  $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
  git -C $PublishRoot commit -m "Update project log $stamp"
  if ($LASTEXITCODE -ne 0) { throw 'Commit failed.' }
  Write-Host 'Committed local changes.'
} else {
  Write-Host 'No changes to commit.'
}

$remote = git -C $PublishRoot remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($remote)) {
  Write-Warning 'Remote "origin" is not set. Set it with:'
  Write-Warning '  git -C "D:\睿谊的WPS\Ferrariwork\CRF\发布\crf-project-log" remote add origin https://github.com/Ferrari-Serena/crf-project-log.git'
  Write-Warning 'Then run this script again to push.'
} else {
  git -C $PublishRoot push -u origin main
  if ($LASTEXITCODE -ne 0) { throw 'Push failed. Pull or rebase may be required.' }
  Write-Host 'Pushed to origin.'
}