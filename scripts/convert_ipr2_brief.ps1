param(
    [string]$PdfPath = 'reports/IPR2/IPR2_BRIEF.pdf',
    [string]$OutputPath = 'reports/IPR2/IPR2_BRIEF.pptx'
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$pdf = (Resolve-Path -LiteralPath (Join-Path $workspace $PdfPath)).Path
$output = Join-Path $workspace $OutputPath
$build = Join-Path $workspace ('tmp/ipr2_pptx_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $build -Force | Out-Null

# Render the source PDF at presentation resolution. Keeping each page intact
# preserves the original mathematical notation, citations, and page design.
& pdftoppm -r 300 -png $pdf (Join-Path $build 'page')
if ($LASTEXITCODE -ne 0) { throw "pdftoppm failed: $LASTEXITCODE" }
$pages = @(Get-ChildItem -LiteralPath $build -Filter 'page-*.png' | Sort-Object Name)
if ($pages.Count -ne 25) { throw "Expected 25 PDF pages; found $($pages.Count)" }

$powerpoint = $null
$presentation = $null
try {
    $powerpoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerpoint.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    for ($index = 0; $index -lt $pages.Count; $index++) {
        $slide = $presentation.Slides.Add($index + 1, 12) # ppLayoutBlank
        $null = $slide.Shapes.AddPicture($pages[$index].FullName, 0, -1, 0, 0, 960, 540)
    }

    $presentation.SaveAs($output, 24) # ppSaveAsOpenXMLPresentation
    for ($index = 0; $index -lt $pages.Count; $index++) {
        $preview = Join-Path $build ('check-{0:D2}.png' -f ($index + 1))
        $presentation.Slides.Item($index + 1).Export($preview, 'PNG', 1920, 1080)
    }
    Write-Output "Saved $($presentation.Slides.Count) slides to $output"
    Write-Output "PowerPoint previews: $build"
}
finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $powerpoint) { $powerpoint.Quit() }
}
