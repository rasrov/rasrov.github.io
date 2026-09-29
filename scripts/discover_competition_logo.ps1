param(
    [string]$EventId = '23425',
    [string]$SearchTerms = 'masters world'
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$events = (Get-Content -LiteralPath (Join-Path $repoRoot 'data/competitions.json') -Raw -Encoding UTF8 | ConvertFrom-Json).events
$event = $events | Where-Object { [string]$_.id -eq $EventId } | Select-Object -First 1
if (-not $event) { throw 'Unknown event ID' }
$source = Invoke-WebRequest $event.url -UseBasicParsing -TimeoutSec 30
$promoter = $source.Links | Where-Object { $_.outerHTML -match 'View Promoter Website' } | Select-Object -First 1 -ExpandProperty href
if (-not $promoter) { throw 'No promoter link found' }
Start-Sleep -Seconds 10
$promoterPage = Invoke-WebRequest $promoter -UseBasicParsing -TimeoutSec 30
$base = $promoterPage.BaseResponse.ResponseUri.AbsoluteUri
$terms = $SearchTerms -split '\s+'
function Find-EventLinks($page) {
    @($page.Links | Where-Object {
        $link = $_
        $link.href -match '/contest/' -and @($terms | Where-Object { $link.href -notmatch [regex]::Escape($_) }).Count -eq 0
    } | Select-Object -ExpandProperty href -Unique)
}
$links = Find-EventLinks $promoterPage
if (-not $links.Count) {
    Start-Sleep -Seconds 10
    $search = Invoke-WebRequest ($base.TrimEnd('/') + '/?s=' + [uri]::EscapeDataString($SearchTerms)) -UseBasicParsing -TimeoutSec 30
    $links = Find-EventLinks $search
}
if ($links.Count -ne 1) { throw "Ambiguous event page: $($links.Count) candidates; manual review required" }
$pageUrl = ([uri]::new([uri]$base, $links[0])).AbsoluteUri
Start-Sleep -Seconds 10
$page = Invoke-WebRequest $pageUrl -UseBasicParsing -TimeoutSec 30
$candidates = @($page.Images | ForEach-Object {
    $src = $_.src
    if ($_.'data-cvpsrc') { $src = $_.'data-cvpsrc' }
    if ($src) {
        $url = ([uri]::new([uri]$pageUrl, $src)).AbsoluteUri
        $score = 0
        foreach ($term in $terms) { if (($url + ' ' + $_.alt) -match [regex]::Escape($term)) { $score += 10 } }
        if ($url -match 'poster|flyer|banner') { $kind = 'poster'; } elseif ($url -match 'logo') { $kind = 'logo-candidate'; } else { $kind = 'unclassified' }
        [pscustomobject]@{url=$url;alt=$_.alt;score=$score;kind=$kind}
    }
} | Sort-Object score -Descending)
$result = [ordered]@{event_id=$EventId;event_name=$event.name;source=$event.url;promoter=$promoter;event_page=$pageUrl;status='needs_visual_review';candidates=$candidates}
$out = Join-Path $repoRoot "docs/logo-discovery-$EventId.json"
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $out -Encoding UTF8
Write-Output "Report: $out"
$candidates | Select-Object -First 3 url,score,kind | Format-List

