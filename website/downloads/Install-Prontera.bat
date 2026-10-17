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
# WARP patches added on top of ROenglishRE's 2019-06 session (NoGNJoyLaunch: the game must not open Gravity's
# website ro.gnjoy.com when it closes). Never add encryption patches:
# rAthena keeps packet obfuscation on for this client.
$ExtraPatches = @('DataFolderFirst', 'NoHShield', 'NoCDefender', 'NoAdminNeeded', 'HideLicense', 'CustomWinTitle', 'NoGNJoyLaunch')

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

# ROenglishRE's lua tables as of 2022-01-25 ("Default Client Date Update to 2021-11-03"): the set made for this exe
# and kRO's data of that month. Master's copies follow kRO of today and use pet, status-icon and map names this exe and
# data.grf do not have (Lua errors "PetInfo table index is nil", "StateIconInfo", "queryNavi_MapInfo").
# Each line is the git blob id and the path under data\luafiles514\lua files.
$RoEnglishLuaCommit = 'db598f1d0f120f8027f9ab4652042eafb6257e73'
$RoEnglishLuaFiles = @'
10c3c6a209d8f025c59fb83108c4ff162704cdca Enchant/EnchantList.lub
fdb71e97e1c21d0162f9e99f5b4eb94dd6789c67 ItemDBNameTbl.lub
a9f67691887343de9cf6db11aa8bb93b594cab28 ItemReform/ItemReformSystem.lub
3047b4faa0d02c0bec6c5d6badd0e2919e87349e admin/pcidentity.lub
c5fc985c8e8b81c56ef7987968a6b436f8ee166c admin/pcjobname.lub
e569a801a8d0c7e578ac85b452d4bb05bf8c89a1 admin/pcjobnamegender.lub
1b0000427101630caca5942838ecc4b94403f796 agit/agitconfig.lub
a8df12d446c442dd4deb3de5411811492abbeee6 battlefield/battlefieldinfo.lub
6435ae8bf74cfd75f9ed4a83813c26d5901672ed datainfo/DrawItemOnAura.lub
317583248b539425b323d0eadf6dadc3c6f4194a datainfo/LapineUpgradeBox.lub
94c84a50ec3510b71da8ed25405311a4ed7b98a2 datainfo/TB_Layer_Priority.lub
92c121ecef67c62bcc76d215cfdbb4e7bde5d1ca datainfo/accessoryid.lub
380eabf1f859e928db0ee769183b55f3a7df20a3 datainfo/accname.lub
0c812120d23e3b8470e2487142260a805800351f datainfo/accname_eng.lub
07f61daf9bf70a425ed2e6861eeab3a256df1f78 datainfo/accname_f.lub
07f7bdfa4b3cc6b28d0ca8131969c542236e7694 datainfo/addrandomoption_f.lub
08dc09da6082d519d091c21d53495d3bb7946667 datainfo/addrandomoptionnametable.lub
baf9e47d68ba39b42c67bb791c99299a6205dd7f datainfo/changedirectorylist.lub
bd8543ad656b39717012657be7efe10ad97db511 datainfo/enumvar.lub
4b61178240de56ba3ef2eb0739045dcf7b1b424d datainfo/exceptionitemproducer.lub
4abdd86b53bf179916699fd66eabe6c896c5d47f datainfo/helpmsgstr.lub
a34786defc8c79ec36159c2f1dbe366981fef420 datainfo/jobidentity.lub
1c664024b3c02460b51fd5610ea67e8e141e05e3 datainfo/jobname.lub
add33d16bd2e12cd860c6e5ecd37bab72e9ce1f2 datainfo/jobname_f.lub
87f981b74cdd8f5cc2feeb7c9e6dafe20414192d datainfo/kaframovemapservicelist.lub
6e5079e5c4943b224c0e736a7a3984a3aeefb34d datainfo/kaframovemapservicelist_f.lub
24fd674832f313d9c64894a309f3e782ba94b54b datainfo/lapineddukddakbox.lub
5788a41d2a3edd1ebc04bf56d3927f92dfa6e733 datainfo/npcidentity.lub
61e1347c063e1cc26a27be0a1f0f3ac2601914cb datainfo/npclocationradius.lub
1e5042a748648b0f09aacbf43194c95ad88585b2 datainfo/npclocationradius_f.lub
f3dd5b041ff087786979d118806cf31fc85f220e datainfo/pcjobnamegender.lub
d1fc262a604f4c3d5f9d7b8ade0b84ada8242dd2 datainfo/pcjobnamegender_f.lub
7cb34fec8bf0e699cab17afcf61e5096f8fcc67c datainfo/petinfo.lub
0564d5727a2b2af0ab1883fd68569d310f9e415a datainfo/questinfo_f.lub
3f77c717c488be2ff7c2c6c49dbe7b14d4974515 datainfo/shadowtable.lub
adefb969fe53bc6b7980fd446614e9e6d00e7159 datainfo/shadowtable_f.lub
5818d2c8d978a362b0f5dad574f57ec12740cbdd datainfo/spriterobeid.lub
42732cf6bed23479bc526ffb54e9e4bd0937dc43 datainfo/spriterobename.lub
6868b167429cb33a0d2d06e2f42bbe4b387ab3aa datainfo/spriterobename_f.lub
eca7909b85bb24fad28f66df2749665054243ab6 datainfo/tb_cashshop_banner.lub
272e054d7f97ee52a52b447cecd1b07d24154e59 datainfo/titletable.lub
53d5ee76036a08d88ef159f1ad7d6bb31bf10220 datainfo/weapontable.lub
611fd9db39938e14c085456f5b0d83a7a36fdf2b datainfo/weapontable_f.lub
2cf4937c3f61be2d7921239e69d61b88c912628a dressroom/dress_f.lub
40e0c48963be637240f6c1e266ae6b6f6fb53d34 dressroom/jobdresslist.lub
5cc8f080fd1c4dc60684f452214b88bde5b9764e effecttool/forcerendereffect.lub
d1de49eeb9505305a8f5a1a0b6b7e1dff178dc1e entryqueue/entryqueuelist.lub
42887f30acbe4e98ad6caf4ac79a4d0ec4705020 hateffectinfo/hateffectinfo.lub
8860ba8e6b9212293908fc9c2f78990336df84ba msgstring_kr.lub
df3e1d3e9334863fed540207ffb6c2f822b69832 msgstring_kr_s.lub
78ccf6977de75f21e4b9fdc23880c5fa281ee5be navigation/navi_f_krpri.lub
78ccf6977de75f21e4b9fdc23880c5fa281ee5be navigation/navi_f_krsak.lub
9a2361175c8eb061ec6ce8ec84bbfa72812f67b0 navigation/navi_link_krpri.lub
9a2361175c8eb061ec6ce8ec84bbfa72812f67b0 navigation/navi_link_krsak.lub
a8c9640521a3c78c5ac39e15ee51800a2da429f6 navigation/navi_linkdistance_krpri.lub
35caa4ca6a69c2676d9241ee87611f63697d7563 navigation/navi_linkdistance_krsak.lub
3d5a2d563452d09b70bffe6f679f78e4c949bb8e navigation/navi_map_krpri.lub
3d5a2d563452d09b70bffe6f679f78e4c949bb8e navigation/navi_map_krsak.lub
b432dc2b99bad6d65e0e4ea2d020ad1a8f40ef72 navigation/navi_mob_krpri.lub
9ff9552f1f3a5537ba34e0cc250d99648e1702d1 navigation/navi_mob_krsak.lub
b060f41ecf93b8d9c8cbe943cea709a344832a26 navigation/navi_npc_krpri.lub
98c053054767363b09db9cb9e4e4a00328695453 navigation/navi_npc_krsak.lub
d8cd22270d3b1815e0bede4de2b04cfc3d67e29a navigation/navi_npcdistance_krpri.lub
255aebe132c7d472e555701234dff9702060e113 navigation/navi_npcdistance_krsak.lub
e4365ace8e67c30e6c48df7d315a7bf911cefa09 navigation/navi_picknpc_krpri.lub
a00d0380a1879e67a6d2d5a740587ec5dc328ddd navigation/navi_picknpc_krsak.lub
a1aa08245d2c443f6eb223c2d327bad945bfb3fc navigation/navi_scroll_krpri.lub
a1aa08245d2c443f6eb223c2d327bad945bfb3fc navigation/navi_scroll_krsak.lub
90220e6957fb5f479f75d6f7f772a50f43530307 optioninfo/cmdinfo.lub
6fc75ee86364a13a961cb4166f26bdceff7c8f5d optioninfo/optioninfo.lub
74267775535cc1ec90a90b5a926a5baf551967dd optioninfo/optioninfo_f.lub
f708470747c5b3303b75ddd80f4954dde1765a05 service_korea/ExternalSettings_kr.lub
2a27821661b7a4b98cfd5b0cd5fd8295c4859d0b service_korea/ExternalSettings_kr_qm.lub
f708470747c5b3303b75ddd80f4954dde1765a05 service_korea/ExternalSettings_kr_sak.lub
2a27821661b7a4b98cfd5b0cd5fd8295c4859d0b service_korea/ExternalSettings_kr_sak_qm.lub
d2fbc044fd0d1be94a8a1523b7c9c48c59a76781 signboardlist.lub
576e28870162bd53c67717e0e791f267bb6f2075 skilleffectinfo/actorstate.lub
70636a8721722de2be488b2d9a9a5220eb0c094d skilleffectinfo/effectid.lub
a2cd368ea8fac29d02c0cc2b3a7abecf9ea37a29 skilleffectinfo/skilleffectinfo_f.lub
915395f82d92d040090f3ef714da6158bf7bc2c8 skilleffectinfo/skilleffectinfolist.lub
ce2cc59d3868fe4c749af3e89b9bcbf20e5e041f skillinfoz/jobinheritlist.lub
11e83ca1e09b250be142f8613e617a99cbc981e1 skillinfoz/skilldescript.lub
2a1fd34c0025c32ec1436449cbad82360871768d skillinfoz/skillid.lub
6a84ed73f4f5807805a361eae29dafe7197b2669 skillinfoz/skillinfo_f.lub
eaf47e40f97f8c12af18bd0c12c13606836eb375 skillinfoz/skillinfolist.lub
306c54d220ff0480ed6d78f8289ef8a59b24d19e skillinfoz/skilltreeview.lub
0054da14f229781c0288cf0191ba1aa2dc56f7b7 skillinfoz/skilltreeview_web.lub
40cefc40465e7c1fbfe1311cfdceb5220909cd0d skillinfoz/test.lub
00bc16cbdd72d8f1fccaf31c6c8e2a31685a4d98 stateicon/efstids.lub
bf82d2e60330e50ec6cd159b076e5d0c0595755d stateicon/stateiconimginfo.lub
7b3acbca5973dc9dcaa6101f60c2cecf6e56b55e stateicon/stateiconinfo.lub
2829cb7480021735485c17dd1472a25d248b6246 stateicon/stateiconinfo_f.lub
a73a155d9fe9702663ebbe2656c5a0fc18424213 transparentItem/transparentItem.lub
6bc8b7875147084db8fb7baed2ea9e0c80189336 transparentItem/transparentItem_f.lub
5781c374c36674d26161129e2f4abc2b0e592d9a worldviewdata/worldviewdata_f.lub
94d43530655ace50e814b109975c3df3c4206cef worldviewdata/worldviewdata_info.lub
90bf8280412135d01012c5574105cfe6f8018784 worldviewdata/worldviewdata_language.lub
a06c6f8add31321ce27b2ca703f47e4071c6ff8a worldviewdata/worldviewdata_list.lub
09ddd23cad74dafc9c99f3c7d7af2e74204e3352 worldviewdata/worldviewdata_table.lub
'@

function Get-GitBlobId([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    $head = [Text.Encoding]::ASCII.GetBytes("blob $($bytes.Length)`0")
    $sha = [Security.Cryptography.SHA1]::Create()
    try {
        [void]$sha.TransformBlock($head, 0, $head.Length, $null, 0)
        [void]$sha.TransformFinalBlock($bytes, 0, $bytes.Length)
        return -join ($sha.Hash | ForEach-Object { $_.ToString('x2') })
    } finally { $sha.Dispose() }
}

# Downloads the 2022 lua set from GitHub once; files already downloaded with the right content are kept.
function Get-EraLuaFiles {
    $dir = Join-Path $ToolsDir "ROenglishRE-lua-$($RoEnglishLuaCommit.Substring(0, 7))"
    $base = "https://raw.githubusercontent.com/llchrisll/ROenglishRE/$RoEnglishLuaCommit/Renewal/data/luafiles514/lua%20files/"
    $web = New-Object Net.WebClient
    $said = $false
    try {
        foreach ($line in ($RoEnglishLuaFiles -split "`r?`n")) {
            if ($line -notmatch '^([0-9a-f]{40}) (\S+)$') { continue }
            $id = $Matches[1]; $rel = $Matches[2]
            $dest = Join-Path $dir ('data\luafiles514\lua files\' + $rel.Replace('/', '\'))
            if ((Test-Path -LiteralPath $dest) -and (Get-GitBlobId $dest) -eq $id) { continue }
            if (-not $said) { Info 'Downloading the English lua files made for this game version ...'; $said = $true }
            New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
            $url = $base + (($rel -split '/' | ForEach-Object { [Uri]::EscapeDataString($_) }) -join '/')
            $ok = $false; $why = 'the file was different from the expected one'
            for ($try = 1; $try -le 3 -and -not $ok; $try++) {
                try { $web.DownloadFile($url, "$dest.part"); $ok = (Get-GitBlobId "$dest.part") -eq $id }
                catch { $why = $_.Exception.Message }
                if (-not $ok) { Start-Sleep -Seconds 2 }
            }
            if (-not $ok) { throw "Could not download $url ($why). Check the internet connection and run the installer again." }
            Move-Item -LiteralPath "$dest.part" -Destination $dest -Force
        }
    } finally { $web.Dispose() }
    return $dir
}

# Builds what ROenglishRE's Tools\ClientGenerator.bat builds for mode 1 + date 9, without its prompts.
# Its lua tables are then swapped for the 2022 set; master's lua files that set lacks are switched off in the game
# folder (renamed to .off, only where the file there is the copy an earlier run of this installer put in).
function Build-EnglishFiles([string]$RoDir, [string]$LuaDir, [string]$Stage) {
    $tr = Join-Path $RoDir 'Translation'
    if (Test-Path -LiteralPath $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $Stage | Out-Null
    Copy-Tree (Join-Path $tr 'Renewal') $Stage
    foreach ($date in $RoEnglishDates) {
        $src = Join-Path (Join-Path $tr 'Compatibility') $date
        if (Test-Path -LiteralPath (Join-Path $src 'Renewal')) { $src = Join-Path $src 'Renewal' }
        if (Test-Path -LiteralPath $src) { Copy-Tree $src $Stage }
    }
    $lua = Join-Path $Stage 'data\luafiles514'
    $eraLua = Join-Path $LuaDir 'data\luafiles514'
    if (Test-Path -LiteralPath $lua) {
        foreach ($file in (Get-ChildItem -LiteralPath $lua -Recurse -File)) {
            $rel = $file.FullName.Substring($lua.Length).TrimStart('\')
            if (Test-Path -LiteralPath (Join-Path $eraLua $rel)) { continue }
            $old = Join-Path (Join-Path $GameDir 'data\luafiles514') $rel
            if ((Test-Path -LiteralPath $old) -and (Get-GitBlobId $old) -eq (Get-GitBlobId $file.FullName)) {
                Move-Item -LiteralPath $old -Destination "$old.off" -Force
                Info "Switched off data\luafiles514\$rel (renamed to .off)"
            }
        }
        Remove-Item -LiteralPath $lua -Recurse -Force
    }
    Copy-Tree $eraLua $lua
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

# ROenglishRE's translated button images live in data\texture\<Korean folder>, written by the kRO/ROenglishRE copy
# as cp949 bytes shown as Latin-1 (a folder name made of accented Latin letters). The exe opens files with the ANSI
# APIs, so on a Windows whose "language for non-Unicode programs" is not Korean or Western it asks for the same bytes
# read as that code page (Thai: cp874), finds nothing, and the buttons stay Korean. Make a twin copy under the name
# the exe asks for. Originals are never touched or deleted; any problem only prints a warning.
function Add-AnsiTextureTwin {
    try {
        $acp = [int](Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage' -Name ACP).ACP
        if ($acp -eq 949 -or $acp -eq 1252 -or $acp -eq 28591) { return }
        $latin1 = [Text.Encoding]::GetEncoding(28591)
        $ansi = [Text.Encoding]::GetEncoding($acp, [Text.EncoderFallback]::ExceptionFallback, [Text.DecoderFallback]::ExceptionFallback)
        $odd = '[' + [char]0x80 + '-' + [char]0xFF + ']'
        $rename = { param([string]$n) if ($n -match $odd) { $ansi.GetString($latin1.GetBytes($n)) } else { $n } }
        $tex = Join-Path $GameDir 'data\texture'
        if (-not (Test-Path -LiteralPath $tex)) { return }
        $copied = 0
        foreach ($dir in @(Get-ChildItem -LiteralPath $tex -Directory | Where-Object { $_.Name -match $odd })) {
            $dst = Join-Path $tex (& $rename $dir.Name)
            if ($dst -eq $dir.FullName) { continue }
            foreach ($file in Get-ChildItem -LiteralPath $dir.FullName -Recurse -File) {
                $rel = $file.FullName.Substring($dir.FullName.Length + 1)
                $newRel = (($rel -split '\\') | ForEach-Object { & $rename $_ }) -join '\'
                $target = Join-Path $dst $newRel
                New-Item -ItemType Directory -Force -Path (Split-Path $target -Parent) | Out-Null
                Copy-Item -LiteralPath $file.FullName -Destination $target -Force
                $copied++
            }
        }
        if ($copied -gt 0) { Info "Copied $copied English button images for Windows code page $acp." }
    } catch {
        Warn "Could not prepare English buttons for this Windows language ($($_.Exception.Message)). The game still works; a few buttons may stay Korean."
    }
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
            # No question: a fresh copy is the only fix and changes nothing in the old folder (players closed the window at a Y/N prompt).
            Info "Installing a fresh copy of the game to $fresh instead (the big download is reused; $GameDir is left as it is)."
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
    $luaDir = Get-EraLuaFiles
    $stage = Join-Path $ToolsDir 'client-files'
    Build-EnglishFiles $roDir $luaDir $stage
    Copy-Tree $stage $GameDir
    Add-SakrayLubs
    Add-AnsiTextureTwin
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

# A fresh kRO install has no screen settings yet, and the game then stops with "Cannot init d3d OR grf file has
# problem". kRO's Setup.exe writes them (to HKLM, so Windows asks for admin), so open it once while they are missing.
function Test-GraphicsSettings {
    foreach ($key in @('HKLM:\SOFTWARE\WOW6432Node\Gravity Soft\Ragnarok', 'HKLM:\SOFTWARE\Gravity Soft\Ragnarok')) {
        $p = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
        if ($p -and $p.WIDTH -and $p.HEIGHT) { return $true }
    }
    return $false
}

function Set-Graphics {
    if (Test-GraphicsSettings) { Info 'Graphics settings found.'; return }
    $setup = Join-Path $GameDir 'Setup.exe'
    if (-not (Test-Path -LiteralPath $setup)) { Warn "Graphics are not set and $setup is missing. Run the installer again."; return }
    Warn 'Graphics are not set yet, so the Gravity setup window opens now. Click Yes if Windows asks, then choose'
    Info '  your graphics card (not a projector), 1024x768, window mode, and click OK.'
    try { Start-Process -FilePath $setup -WorkingDirectory $GameDir -Wait }
    catch { Warn "Setup.exe did not run: $($_.Exception.Message)" }
    if (Test-GraphicsSettings) { Info 'Graphics settings saved.' }
    else { Warn "Graphics are still not set. Before playing, double-click $setup, click Yes and save your settings." }
}

function Test-ServerReachable {
    # Tells the player right away if this PC cannot reach our game server (ISP, router or school/office firewall)
    # so the report is "port X blocked" and not just "cannot play". Warn only; never stops the install.
    Step 'Checking that this PC can reach the game server'
    $bad = @()
    foreach ($port in 6900, 6121, 5121) {
        $client = New-Object System.Net.Sockets.TcpClient
        try {
            $task = $client.ConnectAsync($ServerIP, $port)
            if (-not $task.Wait(6000) -or -not $client.Connected) { $bad += $port }
        } catch { $bad += $port } finally { $client.Close() }
    }
    if ($bad.Count -eq 0) { Info "OK: the game server $ServerIP answers on ports 6900, 6121 and 5121." }
    else {
        Warn ("Cannot reach $ServerIP on port(s) " + ($bad -join ', ') + '. The game will not log in until this is fixed.')
        Warn 'Try another network (phone hotspot). If it works there, your router, ISP or antivirus firewall blocks it. If it fails everywhere, tell the server admin.'
    }
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

        Step '7/7  Desktop and Start menu shortcuts, graphics settings'
        Remove-KroShortcuts
        New-Shortcut (Join-Path ([Environment]::GetFolderPath('Desktop')) "$ServerName.lnk") $exe $GameDir
        New-Shortcut (Join-Path ([Environment]::GetFolderPath('Programs')) "$ServerName.lnk") $exe $GameDir
        Info "Added the $ServerName icon. It starts $exe"
        Set-Graphics
        Test-ServerReachable

        Write-Host ''
        Write-Host "Done! Double-click $ServerName on your desktop to play." -ForegroundColor Green
        Write-Host '  New account: do NOT click Sign Up (it opens Gravity''s website, not ours). In the login box'
        Write-Host '  type your ID with _M (male) or _F (female) at the end, e.g. myname_M, and a password of'
        Write-Host '  6+ characters (use Tab between the boxes), then press Enter. Next time log in without the _M / _F.'
    } catch {
        Write-Host ''
        Write-Host "Install stopped: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Run the installer again to retry. If it keeps failing, send the file $log"
    } finally {
        try { Stop-Transcript | Out-Null } catch { }
    }
}

if (-not $env:PRONTERA_NO_MAIN) { Invoke-Main }
