$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $workspace 'reports/IPR2/IPR2_BRIEF_EDITABLE.pptx'
$testCopy = Join-Path $workspace 'tmp/ipr2_editability_test.pptx'
Copy-Item -LiteralPath $source -Destination $testCopy -Force

$powerpoint = $null
$presentation = $null
try {
    $powerpoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerpoint.Presentations.Open($testCopy, $false, $false, $false)
    if ($presentation.Slides.Count -ne 25) { throw 'Slide count mismatch' }

    $title = $presentation.Slides.Item(1).Shapes | Where-Object {
        $_.HasTextFrame -ne 0 -and $_.TextFrame.TextRange.Text -eq 'IPR 2 Decision Brief'
    } | Select-Object -First 1
    if ($null -eq $title) { throw 'Native title text box missing' }
    $title.TextFrame.TextRange.Text = 'IPR 2 Decision Brief QA'

    $tableShape = $presentation.Slides.Item(2).Shapes | Where-Object { $_.HasTable -ne 0 } | Select-Object -First 1
    if ($null -eq $tableShape) { throw 'Native table missing' }
    $tableShape.Table.Cell(2, 1).Shape.TextFrame.TextRange.Text = 'Editable row QA'
    $presentation.Save()
    $presentation.Close()
    $presentation = $powerpoint.Presentations.Open($testCopy, $true, $false, $false)

    $titleRead = $presentation.Slides.Item(1).Shapes | Where-Object {
        $_.HasTextFrame -ne 0 -and $_.TextFrame.TextRange.Text -eq 'IPR 2 Decision Brief QA'
    } | Select-Object -First 1
    $tableRead = $presentation.Slides.Item(2).Shapes | Where-Object { $_.HasTable -ne 0 } | Select-Object -First 1
    if ($null -eq $titleRead -or $tableRead.Table.Cell(2, 1).Shape.TextFrame.TextRange.Text -ne 'Editable row QA') {
        throw 'PowerPoint edit did not persist'
    }
    Write-Output 'PowerPoint native title and table cell edits persisted after save/reopen.'
}
finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $powerpoint) { $powerpoint.Quit() }
}
