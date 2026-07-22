# minethon setup - run once per student PC.
$ErrorActionPreference = 'Stop'

function Group-For([int]$n) {
    if (($n -ge 1 -and $n -le 10) -or $n -eq 61) { return 1 }
    elseif (($n -ge 11 -and $n -le 16) -or ($n -ge 20 -and $n -le 23) -or $n -eq 62) { return 2 }
    elseif (($n -ge 17 -and $n -le 19) -or ($n -ge 24 -and $n -le 29) -or ($n -ge 63 -and $n -le 64)) { return 3 }
    elseif (($n -ge 31 -and $n -le 37) -or ($n -ge 41 -and $n -le 44)) { return 4 }
    elseif (($n -ge 38 -and $n -le 40) -or ($n -ge 45 -and $n -le 51) -or $n -eq 65) { return 5 }
    elseif (($n -ge 52 -and $n -le 60) -or ($n -ge 66 -and $n -le 67)) { return 6 }
    else { return 0 }
}

$group = 0
$computer = 0
$hostName = $env:COMPUTERNAME
if ($hostName -match 'CSIE-PC(\d+)') {
    $computer = [int]$matches[1]
    $group = Group-For $computer
}

if ($group -gt 0) {
    Write-Host "detected $hostName -> group=$group, computer=$computer"
} else {
    $group = Read-Host "group number"
    $computer = Read-Host "computer number"
    if ($group -notmatch '^\d+$' -or $computer -notmatch '^\d+$') {
        Write-Error "digits only"; exit 1
    }
    $group = [int]$group
    $computer = [int]$computer
}

$path = Join-Path $HOME ".htsdg.json"
$json = "{""group"": $group, ""computer"": $computer}"
# Write UTF-8 WITHOUT a BOM. Set-Content -Encoding UTF8 adds a BOM on Windows
# PowerShell 5.1, which then breaks json parsing on the Python side. WriteAllText
# with an explicit no-BOM UTF8Encoding works on both PS 5.1 and 7.
[System.IO.File]::WriteAllText($path, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "wrote $path (group=$group, computer=$computer)"
