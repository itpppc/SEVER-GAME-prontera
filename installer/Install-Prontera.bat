<# :
@echo off
rem SEVER GAME Prontera - one-click game installer. Double-click this file.
rem The lines below start PowerShell on this same file; the installer itself is the PowerShell part.
setlocal
title Prontera game installer
set "PRONTERA_SELF=%~f0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ([IO.File]::ReadAllText($env:PRONTERA_SELF))"
echo.
pause
exit /b
#>

# ---------------------------------------------------------------------------
# SEVER GAME Prontera: one-click game client installer for Windows 10/11.
#
# Everything is downloaded from its original source (Gravity's official kRO
# installer, nemo.herc.ws, python.org, Microsoft, GitHub) and the game exe is
# patched on this PC, so nothing from Gravity is re-hosted by us.
# Safe to run again: finished steps are skipped and downloads resume.
# Docs: docs/CLIENT.md
# ---------------------------------------------------------------------------

# ===== Settings =====
$ServerIP   = '54.206.105.93'   # game server public IP (PUBLIC_IP in the server .env)
$ServerName = 'Prontera'        # server list name, window title, exe and shortcut name
$GameDir    = 'C:\RO'
$ToolsDir   = 'C:\RO-tools'
# ====================
if ($env:PRONTERA_GAME_DIR)  { $GameDir  = $env:PRONTERA_GAME_DIR }
if ($env:PRONTERA_TOOLS_DIR) { $ToolsDir = $env:PRONTERA_TOOLS_DIR }

$Urls = @{
    KRO       = 'http://rofull.gnjoy.com/RAG_SETUP_220120.exe'
    VcRedist  = 'https://aka.ms/vs/17/release/vc_redist.x86.exe'
    Python    = 'https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi'
    Get4      = 'http://nemo.herc.ws/get4.py'
    RoEnglish = 'https://github.com/llchrisll/ROenglishRE/archive/refs/heads/master.zip'
    Warp      = 'https://github.com/Neo-Mind/WARP/archive/refs/heads/rock_win32.zip'
}
# The exe rAthena PACKETVER 20211103 targets (rAthena PR #6431). Other builds of the same day do not work.
$ExeName = '2021-11-03_Ragexe_1635926200'
$ExeHash = '7d6d0f5400b5cfc8fe6aa366fa293f310f54e3580f0baef5dae617f7b7b575cf'
# ROenglishRE ClientGenerator.bat, mode 1 (Renewal) + date 9 (2021-10-28), copies these in this order.
$RoEnglishDates = @('2017-06-14', '2017-12-13', '2018-06-20', '2019-06-05', '2020-09-02', '2021-10-28')
# WARP patches added on top of ROenglishRE's 2019-06 session. Never add encryption patches:
# rAthena keeps packet obfuscation on for this client.
$ExtraPatches = @('DataFolderFirst', 'NoHShield', 'NoCDefender', 'NoAdminNeeded', 'HideLicense', 'CustomWinTitle')

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Step([string]$Text) { Write-Host ''; Write-Host "==> $Text" -ForegroundColor Cyan }
function Info([string]$Text) { Write-Host "    $Text" }
function Warn([string]$Text) { Write-Host "    ! $Text" -ForegroundColor Yellow }

function Get-RemoteSize([string]$Url) {
    $ErrorActionPreference = 'Continue'
    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) { return $null }
    $headers = & curl.exe -sIL --max-time 30 $Url
    # Trust only the final response after redirects, and only if it is a 200.
    $status = 0; $len = $null
    foreach ($h in $headers) {
        if ($h -match '^HTTP/\S+\s+(\d{3})') { $status = [int]$Matches[1]; $len = $null }
        elseif ($h -match '^Content-Length:\s*(\d+)') { $len = [int64]$Matches[1] }
    }
    if ($status -eq 200 -and $len -gt 0) { return $len }
    return $null
}

function Get-File([string]$Url, [string]$Dest) {
    $ErrorActionPreference = 'Continue'
    $name = Split-Path $Dest -Leaf
    $part = "$Dest.part"
    $remote = Get-RemoteSize $Url
    if (Test-Path -LiteralPath $Dest) {
        $local = (Get-Item -LiteralPath $Dest).Length
        if (-not $remote -or $local -eq $remote) { Info "Already downloaded: $name"; return }
        if ($local -lt $remote) { Move-Item -LiteralPath $Dest -Destination $part -Force -ErrorAction Stop }   # resume it
        else { Remove-Item -LiteralPath $Dest -Force -ErrorAction Stop }
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $Dest -Parent) -ErrorAction Stop | Out-Null
    Info "Downloading $name ..."
    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
        Invoke-WebRequest -Uri $Url -OutFile $part -UseBasicParsing -ErrorAction Stop
    } else {
        $code = 1
        for ($try = 1; $try -le 3; $try++) {
            & curl.exe -L --fail --retry 3 --retry-delay 5 -C - -o $part $Url
            $code = $LASTEXITCODE
            if ($code -eq 0) { break }
            # 33/36: the server cannot resume, so start this file again from zero.
            if ($code -eq 33 -or $code -eq 36) { Remove-Item -LiteralPath $part -Force -ErrorAction SilentlyContinue }
            Warn "Download stopped (curl error $code), trying again ($try/3) ..."
            Start-Sleep -Seconds 5
        }
        if ($code -ne 0) { throw "Could not download $Url (curl error $code). Check the internet connection and run the installer again; it continues where it stopped." }
    }
    if ($remote -and (Get-Item -LiteralPath $part).Length -ne $remote) {
        throw "$name is incomplete. Run the installer again; it continues where it stopped."
    }
    Move-Item -LiteralPath $part -Destination $Dest -Force -ErrorAction Stop
}

function Expand-Zip([string]$Zip, [string]$Dest, [string]$Marker) {
    $ErrorActionPreference = 'Continue'
    Info "Unpacking $(Split-Path $Zip -Leaf) ..."
    New-Item -ItemType Directory -Force -Path $Dest -ErrorAction Stop | Out-Null
    if (Get-Command tar.exe -ErrorAction SilentlyContinue) { & tar.exe -xf $Zip -C $Dest | Out-Host }
    if (-not (Test-Path -LiteralPath $Marker)) { Expand-Archive -LiteralPath $Zip -DestinationPath $Dest -Force -ErrorAction Stop }
    if (-not (Test-Path -LiteralPath $Marker)) { throw "Unpacking $Zip failed. Delete it and run the installer again." }
}

# Merge-copies a folder tree, overwriting files (like xcopy /E /Y).
function Copy-Tree([string]$From, [string]$To) {
    $ErrorActionPreference = 'Continue'
    & robocopy.exe $From.TrimEnd('\') $To.TrimEnd('\') /E /IS /IT /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copying $From to $To failed (robocopy $LASTEXITCODE)." }
}

function Test-GameDir([string]$Dir) {
    return ($Dir -and (Test-Path -LiteralPath (Join-Path $Dir 'data.grf')))
}

# Folders found broken in this run (patched by the kRO updater); a fresh copy goes elsewhere.
$BrokenDirs = New-Object System.Collections.Generic.List[string]

# Remembers the folder of the working copy, so later runs find it before a broken one.
function Get-GameDirFile { return Join-Path $ToolsDir 'game-dir.txt' }

function Find-GameDir {
    $candidates = @()
    $remembered = Get-GameDirFile
    if (Test-Path -LiteralPath $remembered) { $candidates += (Get-Content -LiteralPath $remembered -TotalCount 1) }
    $candidates += $GameDir
    foreach ($root in @('C:\Gravity', "${env:ProgramFiles(x86)}\Gravity", "$env:ProgramFiles\Gravity")) {
        foreach ($leaf in @('Ragnarok', 'RagnarokOnline', 'Ragnarok Online')) { $candidates += (Join-Path $root $leaf) }
    }
    $uninstall = @('HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
                   'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
                   'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*')
    foreach ($key in $uninstall) {
        Get-ItemProperty -Path $key -ErrorAction SilentlyContinue |
            Where-Object { ($_.DisplayName -match 'Ragnarok' -or $_.Publisher -match 'Gravity') -and $_.InstallLocation } |
            ForEach-Object { $candidates += $_.InstallLocation.TrimEnd('\') }
    }
    foreach ($dir in $candidates) { if ((Test-GameDir $dir) -and $BrokenDirs -notcontains $dir.TrimEnd('\')) { return $dir } }
    return $null
}

# The 2021 exe reads GRF 0x200 only. kRO's updater rewrites the GRFs: into a newer format it cannot read,
# or half-written if the updater is stopped. Returns $null when the file looks fine, otherwise the reason.
function Get-GrfProblem([string]$Grf) {
    try { $fs = [IO.File]::Open($Grf, 'Open', 'Read', 'Read') }
    catch { throw "$Grf is in use. Close the game and the Korean updater (press Ctrl+Shift+Esc, right-click Ragnarok, End task), then run the installer again." }
    try {
        # GRF 0x200 offsets are 32-bit, so the 2021 exe crashes on a file over 4 GB. kRO's updater grows data.grf
        # past that when it patches it with years of newer data, while the header stays 0x200.
        if ($fs.Length -gt [uint32]::MaxValue) { return ('it has grown to {0:N1} GB, so the Korean updater has patched it with newer data' -f ($fs.Length / 1GB)) }
        $head = New-Object byte[] 46
        if ($fs.Read($head, 0, 46) -ne 46) { return 'the file is cut off' }
        if ([Text.Encoding]::ASCII.GetString($head, 0, 15) -ne 'Master of Magic') { return 'it is not a GRF file' }
        $ver = [BitConverter]::ToUInt32($head, 42)
        if ($ver -gt 0x200) { return ('it is in a newer format (0x{0:X})' -f $ver) }
        if ($ver -lt 0x200) { return $null }
        # 0x200 layout: the zlib-packed file list sits at 46 + offset, after its packed and real sizes.
        $table = [int64][BitConverter]::ToUInt32($head, 30) + 46
        if ($table + 8 -gt $fs.Length) { return 'its file list is missing' }
        $fs.Position = $table
        $sizes = New-Object byte[] 8
        [void]$fs.Read($sizes, 0, 8)
        $packed = [BitConverter]::ToUInt32($sizes, 0)
        $real = [BitConverter]::ToUInt32($sizes, 4)
        if ($packed -lt 3 -or $table + 8 + $packed -gt $fs.Length) { return 'its file list is cut off' }
        $fs.Position = $table + 10   # skip the 2-byte zlib header
        $z = New-Object IO.Compression.DeflateStream($fs, [IO.Compression.CompressionMode]::Decompress, $true)
        $buf = New-Object byte[] 1MB
        $total = [int64]0
        try {
            while (($n = $z.Read($buf, 0, $buf.Length)) -gt 0) { $total += $n }
        } catch { return 'its file list is damaged' } finally { $z.Dispose() }
        if ($total -ne $real) { return 'its file list is damaged' }
        return $null
    } finally { $fs.Dispose() }
}

function Get-GameFilesProblem {
    foreach ($name in @('data.grf', 'rdata.grf')) {
        $grf = Join-Path $GameDir $name
        if (-not (Test-Path -LiteralPath $grf)) { continue }
        Info "Checking $name ..."
        $why = Get-GrfProblem $grf
        if ($why) { return "$name cannot be used: $why." }
    }
    return $null
}

# The kRO updater (Ragnarok.exe, the window with the START button) and anything else started from the game folder.
function Stop-GameProcesses {
    $prefix = $GameDir.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    $procs = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -eq 'Ragnarok' -or ($_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) })
    if (-not $procs.Count) { return }
    foreach ($p in $procs) {
        Info "Closing $($p.ProcessName) so the game files can be checked ..."
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    $left = @($procs | Where-Object { Get-Process -Id $_.Id -ErrorAction SilentlyContinue })
    if ($left.Count) {
        throw ("Could not close {0}. Press Ctrl+Shift+Esc, right-click it, choose End task, then run the installer again." -f (($left | ForEach-Object { $_.ProcessName }) -join ', '))
    }
}

# A folder for a fresh copy of the game next to a broken one: C:\RO, else C:\RO2, C:\RO3, ...
function Get-FreshGameDir([string]$Broken) {
    $base = 'C:\RO'
    for ($i = 1; $i -lt 10; $i++) {
        $dir = if ($i -eq 1) { $base } else { "$base$i" }
        if ($dir.TrimEnd('\') -ne $Broken.TrimEnd('\') -and -not (Test-Path -LiteralPath (Join-Path $dir 'data.grf'))) { return $dir }
    }
    throw "No free folder for a fresh copy of the game. Delete $Broken and run the installer again."
}

# kRO's own icons start its updater, which breaks the game files for our server, so only our icon stays.
function Remove-KroShortcuts {
    $prefix = $GameDir.TrimEnd('\') + '\'
    $shell = New-Object -ComObject WScript.Shell
    $places = @(
        @{ Dir = [Environment]::GetFolderPath('Desktop');                Deep = $false },
        @{ Dir = [Environment]::GetFolderPath('CommonDesktopDirectory'); Deep = $false },
        @{ Dir = [Environment]::GetFolderPath('Programs');               Deep = $true },
        @{ Dir = [Environment]::GetFolderPath('CommonPrograms');         Deep = $true })
    foreach ($place in $places) {
        if (-not $place.Dir -or -not (Test-Path -LiteralPath $place.Dir)) { continue }
        foreach ($link in @(Get-ChildItem -LiteralPath $place.Dir -Filter '*.lnk' -Recurse:$place.Deep -ErrorAction SilentlyContinue)) {
            if ($link.BaseName -eq $ServerName) { continue }
            $target = ''
            try { $target = $shell.CreateShortcut($link.FullName).TargetPath } catch { }
            if (-not $target -or -not $target.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { continue }
            if ((Split-Path $target -Leaf) -match '^(unins|setup)') { continue }   # uninstaller and graphics settings are harmless
            try {
                Remove-Item -LiteralPath $link.FullName -Force -ErrorAction Stop
                Info "Removed the kRO icon $($link.Name) (it starts the Korean updater)."
            } catch {
                Warn "Could not remove the kRO icon $($link.FullName). Never use it; use $ServerName."
            }
        }
    }
}

function Test-InnoSetup([string]$Exe) {
    $fs = [IO.File]::OpenRead($Exe)
    try {
        $n = [int][Math]::Min($fs.Length, 4MB)
        $buf = New-Object byte[] $n
        $read = $fs.Read($buf, 0, $n)
    } finally { $fs.Dispose() }
    return ([Text.Encoding]::ASCII.GetString($buf, 0, $read) -match 'Inno Setup')
}

function Test-VcRedistX86 {
    foreach ($key in @('HKLM:\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\X86',
                       'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X86')) {
        $p = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
        if ($p -and $p.Installed -eq 1) { return $true }
    }
    return $false
}

# Builds what ROenglishRE's Tools\ClientGenerator.bat builds for mode 1 + date 9, without its prompts.
function Build-EnglishFiles([string]$RoDir, [string]$Stage) {
    $tr = Join-Path $RoDir 'Translation'
    if (Test-Path -LiteralPath $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $Stage | Out-Null
    Copy-Tree (Join-Path $tr 'Renewal') $Stage
    foreach ($date in $RoEnglishDates) {
        $src = Join-Path (Join-Path $tr 'Compatibility') $date
        if (Test-Path -LiteralPath (Join-Path $src 'Renewal')) { $src = Join-Path $src 'Renewal' }
        if (Test-Path -LiteralPath $src) { Copy-Tree $src $Stage }
    }
}

# kRO's install ships the System\*.lub files of its main exe (X_true.lub, X_True.lub, X_new.lub, X.lub), but a
# Renewal exe like ours asks for the Sakray names (X_sak.lub, X_Sakray.lub, X_sak_new.lub; see WARP CustomPath.qjs).
# Missing ones stop the game ("CPetEvolutionMgr file Init"), so give every main lub its Sakray twins.
# Only kRO's own files are used: they match this exe's era, while ROenglishRE's newer copies list pets and maps
# the 2021 exe does not know (the game crashed with 0xC0000005 when those were used).
function Add-SakrayLubs {
    $sys = Join-Path $GameDir 'System'
    New-Item -ItemType Directory -Force -Path $sys | Out-Null
    $roEnglishHeader = '-- Original translation works of zackdreaver*'
    # _true/_True files first: they are what kRO's own exe of this era reads, so they win over plain X.lub.
    $lubs = @(Get-ChildItem -LiteralPath $sys -Filter '*.lub' -File | Where-Object { $_.BaseName -notmatch '_sak' } |
        Sort-Object @{ Expression = { if ($_.BaseName -match '_true$') { 0 } elseif ($_.BaseName -match '_new$') { 1 } else { 2 } } }, Name)
    $added = 0
    foreach ($lub in $lubs) {
        $base = $lub.BaseName
        if ($base -match '^(.+)_true$') { $names = @("$($Matches[1])_sak.lub", "$($Matches[1])_Sakray.lub") }
        elseif ($base -match '^(.+)_new$') { $names = @("$($Matches[1])_sak_new.lub") }
        else { $names = @("$($base)_sak.lub", "$($base)_Sakray.lub") }
        foreach ($name in $names) {
            $twin = Join-Path $sys $name
            # Keep an existing twin unless an earlier installer filled it with an ROenglishRE copy.
            if ((Test-Path -LiteralPath $twin) -and
                (Get-Content -LiteralPath $twin -TotalCount 1 -ErrorAction SilentlyContinue) -notlike $roEnglishHeader) { continue }
            Copy-Item -LiteralPath $lub.FullName -Destination $twin -Force
            $added++
        }
    }
    Info "Added $added Sakray copies of System lub files."
}

# GRF read order, highest priority first: our own server.grf (optional), then kRO's own list.
function Write-DataIni([string]$Dir, [string]$OriginalIni) {
    $order = @('server.grf')
    if ($OriginalIni -and (Test-Path -LiteralPath $OriginalIni)) {
        foreach ($line in Get-Content -LiteralPath $OriginalIni) {
            if ($line -match '^\s*\d+\s*=\s*(\S.*?)\s*$' -and $order -notcontains $Matches[1]) { $order += $Matches[1] }
        }
    }
    foreach ($grf in @('rdata.grf', 'data.grf')) {
        if ($order -notcontains $grf -and (Test-Path -LiteralPath (Join-Path $Dir $grf))) { $order += $grf }
    }
    $lines = @('[Data]')
    for ($i = 0; $i -lt $order.Count; $i++) { $lines += "$i=$($order[$i])" }
    Set-Content -LiteralPath (Join-Path $Dir 'DATA.INI') -Value $lines -Encoding ASCII
}

# No <passwordencrypt />: it blocks _M/_F account sign-up on rAthena.
function Write-ClientInfo([string]$Path, [string]$ServerType) {
    $images = (0..6 | ForEach-Object { "            <image>loading0$_.jpg</image>" }) -join "`r`n"
    $xml = @"
<?xml version="1.0" encoding="euc-kr" ?>
<clientinfo>
    <desc>Ragnarok Client Information</desc>
    <servicetype>korea</servicetype>
    <servertype>$ServerType</servertype>
    <connection>
        <display>$ServerName</display>
        <address>$ServerIP</address>
        <port>6900</port>
        <version>55</version>
        <langtype>0</langtype>
        <registrationweb>www.ragnarok.com</registrationweb>
        <loading>
$images
        </loading>
        <aid>
            <admin>2000000</admin>
        </aid>
    </connection>
</clientinfo>
"@
    New-Item -ItemType Directory -Force -Path (Split-Path $Path -Parent) | Out-Null
    Set-Content -LiteralPath $Path -Value $xml -Encoding ASCII
}

# Points the client's web service (hotkeys, UI settings, guild emblems) at rAthena's web-server on port 8888.
function Set-AssistAddr([string]$Dir) {
    $latin1 = [Text.Encoding]::GetEncoding(28591)
    $svc = Join-Path $Dir 'data\luafiles514\lua files\service_korea'
    foreach ($file in @('ExternalSettings_kr.lub', 'ExternalSettings_kr_sak.lub')) {
        $path = Join-Path $svc $file
        if (-not (Test-Path -LiteralPath $path)) { continue }
        $text = [IO.File]::ReadAllText($path, $latin1)
        if ($text.StartsWith([string][char]27 + 'Lua')) { Warn "$file is compiled Lua; AssistAddr left unchanged."; continue }
        $new = [regex]::Replace($text, 'AssistAddr\s*=\s*"[^"]*"', "AssistAddr = `"$($ServerIP):8888`"")
        if ($new -ne $text) { [IO.File]::WriteAllText($path, $new, $latin1) }
    }
}

function ConvertTo-YamlQuoted([string]$Text) { return "'" + $Text.Replace("'", "''") + "'" }

# ROenglishRE's WARP session plus our extra patches, window title and source/target exe.
function Write-WarpSession([string]$BaseSession, [string]$OutFile, [string]$FromExe, [string]$ToExe) {
    $titleHex = (($ServerName.ToCharArray() | ForEach-Object { '{0:x2}' -f [int]$_ }) -join '') + '00'
    $existing = @(Get-Content -LiteralPath $BaseSession | ForEach-Object { if ($_ -match '^\s*-\s*(\S+)\s*$') { $Matches[1] } })
    $out = @("from: $(ConvertTo-YamlQuoted $FromExe)", "to: $(ConvertTo-YamlQuoted $ToExe)", '')
    foreach ($line in Get-Content -LiteralPath $BaseSession) {
        if ($line -match '^\s*(from|to)\s*:') { continue }
        $out += $line
        if ($line -match '^inputs:\s*$') {
            $out += '    $customWindowTitle:'
            $out += "        data: '$titleHex'"
            $out += "        display: `"$ServerName`""
            $out += '        type: 10'
            $out += '    '
        }
        if ($line -match '^patches:\s*$') {
            foreach ($p in $ExtraPatches) { if ($existing -notcontains $p) { $out += "    - $p" } }
        }
    }
    Set-Content -LiteralPath $OutFile -Value $out -Encoding ASCII
}

function New-Shortcut([string]$LinkPath, [string]$Target, [string]$WorkDir) {
    if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) { throw "Cannot make the $ServerName icon: $Target does not exist." }
    if (Test-Path -LiteralPath $LinkPath) { Remove-Item -LiteralPath $LinkPath -Force }
    New-Item -ItemType Directory -Force -Path (Split-Path $LinkPath -Parent) | Out-Null
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($LinkPath)
    $lnk.TargetPath = $Target
    $lnk.WorkingDirectory = $WorkDir
    $lnk.IconLocation = "$Target,0"
    $lnk.Description = "$ServerName - Ragnarok Online"
    $lnk.Save()
    $saved = $shell.CreateShortcut($LinkPath).TargetPath
    if (-not $saved -or [IO.Path]::GetFullPath($saved) -ne [IO.Path]::GetFullPath($Target)) {
        throw "The $ServerName icon was not saved correctly: $LinkPath"
    }
}

function Install-Game {
    Step "1/7  Ragnarok base game (official kRO installer from Gravity)"
    $found = Find-GameDir
    if ($found) {
        $script:GameDir = $found
        Info "Found the game in $GameDir"
        Stop-GameProcesses
        $problem = Get-GameFilesProblem
        if ($problem) {
            Warn $problem
            Warn 'This happens when the Korean updater (the window with the START button) runs. Our game exe cannot use these files.'
            $fresh = Get-FreshGameDir $GameDir
            $answer = Read-Host "    Type Y and press Enter to install a fresh copy of the game to $fresh (the big download is reused; $GameDir is left as it is)"
            if ($answer -notmatch '^\s*[Yy]') { throw "Stopped without changes. Run the installer again and type Y to install a fresh copy." }
            $BrokenDirs.Add($GameDir.TrimEnd('\'))
            $script:GameDir = $fresh
            $found = $null
        }
    }
    if (-not $found) {
        $drive = Split-Path -Qualifier $GameDir
        $free = (Get-PSDrive -Name $drive.TrimEnd(':')).Free
        if ($free -lt 12GB) {
            Warn ("Only {0:N1} GB free on {1}. The game needs about 12 GB." -f ($free / 1GB), $drive)
            Read-Host '    Free some space and press Enter to continue (or close this window)' | Out-Null
        }
        $setup = Join-Path $ToolsDir 'RAG_SETUP_220120.exe'
        $earlier = Join-Path $env:USERPROFILE 'Downloads\RAG_SETUP_220120.exe'
        if (-not (Test-Path -LiteralPath $setup) -and (Test-Path -LiteralPath $earlier)) { $setup = $earlier }
        Info 'This file is several GB. If the download stops, run the installer again and it continues.'
        Get-File $Urls.KRO $setup
        New-Item -ItemType Directory -Force -Path $GameDir | Out-Null
        if (Test-InnoSetup $setup) {
            Info "Installing to $GameDir (click Yes if Windows asks) ..."
            Start-Process -FilePath $setup -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', "/DIR=`"$GameDir`"") -Wait
        } else {
            Write-Host ''
            Write-Host '    The official installer is in Korean. Click Yes if Windows asks, then:' -ForegroundColor Green
            Write-Host '      - click the right-hand button at the bottom of each page (Next / I agree)'
            Write-Host "      - when it shows the install folder, change it to  $GameDir"
            Write-Host '      - on the last page, untick anything that starts the game, then finish'
            Write-Host '    Never start the game from the kRO icon: its updater breaks the files for our server.' -ForegroundColor Yellow
            Start-Process -FilePath $setup -Wait
        }
        for ($i = 0; $i -lt 3 -and -not (Find-GameDir); $i++) {
            Read-Host '    Press Enter when the Korean installer has completely finished' | Out-Null
        }
        $found = Find-GameDir
        if (-not $found) {
            Warn "If the Korean installer showed an error, its download is broken: delete $setup and run this installer again."
        }
        while (-not $found) {
            $answer = Read-Host '    Could not find data.grf. Type the folder you installed the game to (for example C:\Gravity\Ragnarok)'
            if (Test-GameDir $answer.Trim('"', ' ')) { $found = $answer.Trim('"', ' ') }
        }
        $script:GameDir = $found
        Info "Game installed in $GameDir"
        Stop-GameProcesses
        $problem = Get-GameFilesProblem
        if ($problem) { throw "$problem The download may be broken: delete $setup, uninstall the game and run the installer again." }
    }
    Stop-GameProcesses
    Set-Content -LiteralPath (Get-GameDirFile) -Value $GameDir -Encoding ASCII
    $updater = Join-Path $GameDir 'Ragnarok.exe'
    if (Test-Path -LiteralPath $updater) {
        Move-Item -LiteralPath $updater -Destination "$updater.off" -Force
        Info 'Turned off the kRO updater (Ragnarok.exe -> Ragnarok.exe.off) so it cannot break the game files.'
    }
}

function Install-Runtime {
    Step '2/7  Microsoft Visual C++ runtime (x86)'
    if (Test-VcRedistX86) { Info 'Already installed.'; return }
    $vc = Join-Path $ToolsDir 'vc_redist.x86.exe'
    Get-File $Urls.VcRedist $vc
    Info 'Installing (click Yes if Windows asks) ...'
    $p = Start-Process -FilePath $vc -ArgumentList @('/install', '/passive', '/norestart') -Wait -PassThru
    if (@(0, 1638, 3010) -notcontains $p.ExitCode) { Warn "The runtime installer returned $($p.ExitCode); continuing." }
}

function Get-GameExe {
    Step "3/7  Game exe $ExeName (downloaded with nemo's get4.py)"
    $exeDir = Join-Path $ToolsDir 'exe'
    $rawExe = Join-Path $exeDir "$ExeName.exe"
    if (Test-Path -LiteralPath $rawExe) { Info 'Already downloaded.'; return $rawExe }
    $py = 'C:\Python27\python.exe'
    if (-not (Test-Path -LiteralPath $py)) {
        $msi = Join-Path $ToolsDir 'python-2.7.15.msi'
        Get-File $Urls.Python $msi
        Info 'Installing Python 2.7, needed once for get4.py (click Yes if Windows asks) ...'
        $p = Start-Process -FilePath 'msiexec.exe' -ArgumentList @('/i', "`"$msi`"", '/passive', '/norestart', 'ALLUSERS=1', 'TARGETDIR=C:\Python27') -Wait -PassThru
        if (-not (Test-Path -LiteralPath $py)) { throw "Python 2.7 did not install (msiexec exit code $($p.ExitCode))." }
    }
    $get4 = Join-Path $exeDir 'get4.py'
    Get-File $Urls.Get4 $get4
    Push-Location $exeDir
    try {
        $ErrorActionPreference = 'Continue'
        & $py -u $get4 $ExeName $ExeHash | Out-Host
    } finally {
        $ErrorActionPreference = 'Stop'
        Pop-Location
    }
    if (-not (Test-Path -LiteralPath $rawExe)) {
        $alt = Get-ChildItem -LiteralPath $exeDir -Recurse -Filter "$ExeName*.exe" | Select-Object -First 1
        if (-not $alt) { throw "get4.py did not produce $ExeName.exe. If antivirus removed it, allow that one file and run the installer again." }
        Copy-Item -LiteralPath $alt.FullName -Destination $rawExe
    }
    return $rawExe
}

function Install-English {
    Step '4/7  English menus and item names (ROenglishRE)'
    $roDir = Join-Path $ToolsDir 'ROenglishRE-master'
    $marker = Join-Path $roDir 'Translation\Renewal\DATA.ini'
    if (-not (Test-Path -LiteralPath $marker)) {
        $zip = Join-Path $ToolsDir 'ROenglishRE.zip'
        Get-File $Urls.RoEnglish $zip
        Expand-Zip $zip $ToolsDir $marker
    }
    $backup = Join-Path $ToolsDir 'backup'
    New-Item -ItemType Directory -Force -Path $backup | Out-Null
    foreach ($f in @('DATA.INI', 'cps.dll', 'CDClient.dll')) {
        $src = Join-Path $GameDir $f
        $dst = Join-Path $backup $f
        if ((Test-Path -LiteralPath $src) -and -not (Test-Path -LiteralPath $dst)) { Copy-Item -LiteralPath $src -Destination $dst }
    }
    $stage = Join-Path $ToolsDir 'client-files'
    Build-EnglishFiles $roDir $stage
    Copy-Tree $stage $GameDir
    Add-SakrayLubs
    Write-DataIni $GameDir (Join-Path $backup 'DATA.INI')
    Info 'Copied the English files and wrote DATA.INI.'
    return $roDir
}

function Set-ServerAddress {
    Step "5/7  Point the game at $ServerName ($ServerIP)"
    Write-ClientInfo (Join-Path $GameDir 'data\clientinfo.xml') 'primary'
    Write-ClientInfo (Join-Path $GameDir 'data\sclientinfo.xml') 'sakray'
    Set-AssistAddr $GameDir
    Info 'Wrote clientinfo.xml and sclientinfo.xml.'
}

function Invoke-Warp([string]$RawExe, [string]$RoDir) {
    Step '6/7  Patch the game exe for our server (WARP)'
    $warpDir = Join-Path $ToolsDir 'WARP-rock_win32'
    $console = Join-Path $warpDir 'win32\WARP_console.exe'
    if (-not (Test-Path -LiteralPath $console)) {
        $zip = Join-Path $ToolsDir 'WARP.zip'
        Get-File $Urls.Warp $zip
        Expand-Zip $zip $ToolsDir $console
    }
    if (-not (Test-Path -LiteralPath $RawExe -PathType Leaf)) { throw "The game exe $RawExe is missing. Run the installer again." }
    $target = Join-Path $GameDir "$ServerName.exe"
    $session = Join-Path $ToolsDir 'prontera-warp.yml'
    Write-WarpSession (Join-Path $RoDir 'Addons\WARP Sessions\2019-06_Translation.yml') $session $RawExe $target
    Stop-GameProcesses
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
    Info 'If WARP asks "Do you want the CDClient DLL copied as well?", type y and press Enter.'
    $warpArgs = @('-using', "`"$session`"", '-from', "`"$RawExe`"", '-to', "`"$target`"")
    Start-Process -FilePath $console -ArgumentList $warpArgs -WorkingDirectory $warpDir -NoNewWindow -Wait
    if (-not (Test-Path -LiteralPath $target)) {
        Warn 'Automatic patching did not finish. WARP opens now; please do these 4 clicks:'
        Info "  1) Source: choose $RawExe and click Load Source"
        Info "  2) Left menu: Session > Load Session file: choose $session"
        Info '  3) Click Apply Patches (answer Yes if it asks to copy CDClient)'
        Info '  4) Close WARP'
        Start-Process -FilePath (Join-Path $warpDir 'win32\WARP.exe') -WorkingDirectory $warpDir -Wait
        if (-not (Test-Path -LiteralPath $target)) {
            $patched = Get-ChildItem -LiteralPath (Split-Path $RawExe -Parent) -Filter '*_patched.exe' |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if (-not $patched) { throw 'The patched exe was not created. Run the installer again.' }
            Copy-Item -LiteralPath $patched.FullName -Destination $target -Force
        }
    }
    # Stub CDClient.dll from WARP replaces kRO's Cheat Defender, which rAthena does not speak.
    Copy-Item -LiteralPath (Join-Path $warpDir 'Inputs\CDClient.dll') -Destination (Join-Path $GameDir 'CDClient.dll') -Force
    Info "Created $target"
    return $target
}

function Invoke-Main {
    New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
    $log = Join-Path $ToolsDir 'install-log.txt'
    try { Start-Transcript -Path $log -Append | Out-Null } catch { }
    try {
        Write-Host "SEVER GAME $ServerName - game installer" -ForegroundColor Green
        Write-Host "Game folder: $GameDir   Tools and downloads: $ToolsDir"
        if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) { Warn 'curl.exe not found; downloads will be slower.' }
        Install-Game
        Install-Runtime
        $rawExe = Get-GameExe
        $roDir = Install-English
        Set-ServerAddress
        $exe = Invoke-Warp $rawExe $roDir

        Step '7/7  Desktop and Start menu shortcuts'
        Remove-KroShortcuts
        New-Shortcut (Join-Path ([Environment]::GetFolderPath('Desktop')) "$ServerName.lnk") $exe $GameDir
        New-Shortcut (Join-Path ([Environment]::GetFolderPath('Programs')) "$ServerName.lnk") $exe $GameDir
        Info "Added the $ServerName icon. It starts $exe"

        Write-Host ''
        Write-Host "Done! Double-click $ServerName on your desktop to play." -ForegroundColor Green
        Write-Host '  New account: type your ID with _M (male) or _F (female) at the end, e.g. myname_M,'
        Write-Host '  with a password of 6+ characters. Then log in again without the _M / _F.'
    } catch {
        Write-Host ''
        Write-Host "Install stopped: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Run the installer again to retry. If it keeps failing, send the file $log"
    } finally {
        try { Stop-Transcript | Out-Null } catch { }
    }
}

if (-not $env:PRONTERA_NO_MAIN) { Invoke-Main }
