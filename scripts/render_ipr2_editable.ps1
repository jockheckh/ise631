param(
    [string]$InputPath = 'reports/IPR2/IPR2_BRIEF_EDITABLE.pptx',
    [string]$PreviewDir = 'tmp/ipr2_editable_preview'
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$inputFile = (Resolve-Path -LiteralPath (Join-Path $workspace $InputPath)).Path
$outputDir = Join-Path $workspace $PreviewDir
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$powerpoint = $null
$presentation = $null
try {
    $powerpoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerpoint.Presentations.Open($inputFile, $true, $false, $false)
    for ($index = 1; $index -le $presentation.Slides.Count; $index++) {
        $preview = Join-Path $outputDir ('slide-{0:D2}.png' -f $index)
        $presentation.Slides.Item($index).Export($preview, 'PNG', 1920, 1080)
    }
    Write-Output "Rendered $($presentation.Slides.Count) slides to $outputDir"
}
finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $powerpoint) { $powerpoint.Quit() }
}
