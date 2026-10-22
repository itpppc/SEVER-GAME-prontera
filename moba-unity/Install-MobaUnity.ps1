# Install-MobaUnity.ps1 - installs Unity and opens the "Suek Lanka MOBA" game (Windows, one command).
# Run in PowerShell:
#   irm https://raw.githubusercontent.com/itpppc/SEVER-GAME-prontera/main/moba-unity/Install-MobaUnity.ps1 | iex
# This file is deliberately plain ASCII with no BOM: "irm | iex" on Windows PowerShell 5.1 breaks on a BOM
# and the console cannot draw Thai glyphs, so all messages here are English. Thai steps are given in the chat.
# Installs only Unity Hub, Unity 6 LTS (to F:\Unity\Editor when drive F exists) and the game project folder.
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Ref  = if ($env:MOBA_REF) { $env:MOBA_REF } else { 'main' }
$Repo = 'itpppc/SEVER-GAME-prontera'
$HasF = Test-Path 'F:\'
$Dest = if ($HasF) { 'F:\ProjectAI\SuekLanka-MOBA' } else { Join-Path $env:USERPROFILE 'SuekLanka-MOBA' }
$EditorRoot = if ($HasF) { 'F:\Unity\Editor' } else { 'C:\Program Files\Unity\Hub\Editor' }
$HubCandidates = @(
    'C:\Program Files\Unity Hub\Unity Hub.exe',
    (Join-Path $env:LOCALAPPDATA 'Programs\Unity Hub\Unity Hub.exe'),
    'C:\Program Files (x86)\Unity Hub\Unity Hub.exe'
)
function Find-Hub { $HubCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1 }

function Say($m) { Write-Host ""; Write-Host ">> $m" -ForegroundColor Yellow }
function Ok($m)  { Write-Host "   $m" -ForegroundColor Green }

Say '1/5 Checking Unity Hub'
$HubExe = Find-Hub
if (-not $HubExe) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        winget install -e --id Unity.UnityHub --accept-package-agreements --accept-source-agreements | Out-Host
        $HubExe = Find-Hub
    }
    if (-not $HubExe) {
        $setup = Join-Path $env:TEMP 'UnityHubSetup.exe'
        Invoke-WebRequest 'https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.exe' -OutFile $setup
        Start-Process $setup -ArgumentList '/S' -Wait
        $HubExe = Find-Hub
    }
}
if (-not $HubExe) { throw 'Could not install Unity Hub. Download it from https://unity.com/download, then run this command again.' }
Ok "Unity Hub found: $HubExe"

Say '2/5 Checking Unity Editor (version 6000 = Unity 6)'
$unity = $null
if (Test-Path $EditorRoot) {
    $unity = Get-ChildItem $EditorRoot -Directory | Where-Object { $_.Name -like '6000.*' } | Sort-Object Name -Descending |
             ForEach-Object { Join-Path $_.FullName 'Editor\Unity.exe' } | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $unity) {
    $ver = $null; $cs = $null
    try {
        $r = Invoke-RestMethod 'https://services.api.unity.com/unity/editor/release/v1/releases?stream=LTS&version=6000&limit=1&order=RELEASE_DATE_DESC&platform=WINDOWS'
        $ver = $r.results[0].version; $cs = $r.results[0].shortRevision
    } catch { Write-Host '   (could not read the latest version from unity.com, asking Unity Hub instead)' }
    if (-not $ver) {
        $list = & $HubExe -- --headless editors -r 2>&1 | Out-String
        $m = [regex]::Match($list, '6000\.\d+\.\d+f\d+')
        if ($m.Success) { $ver = $m.Value }
    }
    if (-not $ver) { throw 'Could not find a Unity 6 version. Install Unity 6 LTS from Unity Hub yourself, then run this command again.' }
    New-Item -ItemType Directory -Force -Path $EditorRoot | Out-Null
    & $HubExe -- --headless install-path -s "$EditorRoot" | Out-Host
    Write-Host "   Installing Unity $ver to $EditorRoot (about 3-5 GB, please wait and keep this window open)"
    if ($cs) { & $HubExe -- --headless install --version $ver --changeset $cs | Out-Host }
    else     { & $HubExe -- --headless install --version $ver | Out-Host }
    $deadline = (Get-Date).AddMinutes(60)
    while (-not (Test-Path (Join-Path $EditorRoot "$ver\Editor\Unity.exe")) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 10 }
    $unity = Join-Path $EditorRoot "$ver\Editor\Unity.exe"
    if (-not (Test-Path $unity)) { throw 'Unity is not finished installing yet. Wait a bit and run the same command again.' }
}
Ok "Unity found: $unity"

Say '3/5 Downloading the game project'
$zip = Join-Path $env:TEMP 'suek-lanka.zip'; $tmp = Join-Path $env:TEMP 'suek-lanka-src'
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
Invoke-WebRequest "https://github.com/$Repo/archive/refs/heads/$Ref.zip" -OutFile $zip
Expand-Archive $zip -DestinationPath $tmp -Force
$src = Get-ChildItem $tmp -Directory | Select-Object -First 1
$proj = Join-Path $src.FullName 'moba-unity'
if (-not (Test-Path $proj)) { throw "Folder moba-unity not found in branch $Ref" }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
robocopy $proj $Dest /E /XD Library Temp Builds Logs UserSettings /NFL /NDL /NJH /NJS | Out-Null
Ok "Project copied to $Dest"

Say '4/5 Opening the project in Unity (first open takes 2-5 minutes)'
Start-Process $unity -ArgumentList @('-projectPath', "`"$Dest`"")

Say '5/5 What is left'
Write-Host '   1) If Unity asks you to sign in, use your Unity ID (free) and choose the Personal (free) license'
Write-Host '   2) Wait until the Unity window opens and stops loading'
Write-Host '   3) Press the Play button at the top center, pick a hero, press Start'
Write-Host ''
Write-Host '   If you see red text in the Unity Console, send a screenshot to Claude in the chat' -ForegroundColor Cyan
