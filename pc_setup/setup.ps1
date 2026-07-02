# minethon setup - run once per student PC.
$ErrorActionPreference = 'Stop'
$group = Read-Host "group number"
$computer = Read-Host "computer number"
if ($group -notmatch '^\d+$' -or $computer -notmatch '^\d+$') {
    Write-Error "digits only"; exit 1
}
$path = Join-Path $HOME ".htsdg.json"
"{""group"": $group, ""computer"": $computer}" | Set-Content -Path $path -Encoding UTF8
Write-Host "wrote $path (group=$group, computer=$computer)"
