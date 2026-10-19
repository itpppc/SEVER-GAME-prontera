# Prontera crash check, for when the game closes right after it starts.
# Starts Prontera.exe like the desktop icon does and records how it ends. If it crashes, it also records where:
# a crash dump from Windows Error Reporting, the exe code around the crash and the file names on the stack.
# The short report goes to C:\RO-tools\crash-report.txt and the clipboard, ready to paste into the support chat.
# Nothing stays changed: the test renames of the data folders and the crash-dump setting are undone at the end.
#
# Run it in PowerShell (as Administrator, so Windows can write the crash dump):
#   [Net.ServicePointManager]::SecurityProtocol='Tls12'; iex (iwr -UseBasicParsing https://raw.githubusercontent.com/itpppc/SEVER-GAME-prontera/main/installer/Check-Prontera.ps1).Content

$ErrorActionPreference = 'Stop'
$ServerName = 'Prontera'
$ToolsDir = 'C:\RO-tools'
$DumpDir = "$ToolsDir\dumps"
$WaitSeconds = 25
$DumpKey = 'SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\Prontera.exe'
$Report = New-Object System.Collections.Generic.List[string]

function Note([string]$Text) { Write-Host $Text; $Report.Add($Text) }
function U32([byte[]]$B, [int64]$O) { return [int64][BitConverter]::ToUInt32($B, [int]$O) }

function Find-Game {
    $dirs = @()
    $lnk = Join-Path ([Environment]::GetFolderPath('Desktop')) "$ServerName.lnk"
    if (Test-Path -LiteralPath $lnk) {
        $target = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk).TargetPath
        if ($target) { $dirs += Split-Path $target -Parent }
    }
    $dirs += 'C:\Gravity\Ragnarok', 'C:\RO'
    if (${env:ProgramFiles(x86)}) { $dirs += Join-Path ${env:ProgramFiles(x86)} 'Gravity\Ragnarok' }
    foreach ($d in $dirs) { if ($d -and (Test-Path -LiteralPath (Join-Path $d "$ServerName.exe"))) { return $d } }
    throw "Could not find $ServerName.exe. Run the installer first."
}

# --- The exe file: sections, file offsets and the strings its code points at ---

function Read-Pe([string]$Path) {
    $x = [IO.File]::ReadAllBytes($Path)
    $pe = [BitConverter]::ToInt32($x, 0x3C)
    $count = [BitConverter]::ToUInt16($x, $pe + 6)
    $optSize = [BitConverter]::ToUInt16($x, $pe + 20)
    $sections = for ($i = 0; $i -lt $count; $i++) {
        $o = $pe + 24 + $optSize + 40 * $i
        $raw = U32 $x ($o + 16)
        [pscustomobject]@{ Va = U32 $x ($o + 12); Size = [Math]::Max((U32 $x ($o + 8)), $raw); Raw = U32 $x ($o + 20); RawSize = $raw }
    }
    return [pscustomobject]@{ Bytes = $x; Base = U32 $x ($pe + 52); ImageSize = U32 $x ($pe + 80); Sections = @($sections) }
}

function Get-FileOffset($Pe, [int64]$Rva) {
    foreach ($s in $Pe.Sections) {
        if ($Rva -ge $s.Va -and $Rva -lt $s.Va + $s.Size) {
            $d = $Rva - $s.Va
            if ($d -lt $s.RawSize) { return $s.Raw + $d }
        }
    }
    return -1
}

# A zero-terminated text at $Rva, or $null when it does not look like text. Korean bytes show as '?'.
function Get-CString($Pe, [int64]$Rva) {
    $off = Get-FileOffset $Pe $Rva
    if ($off -lt 0) { return $null }
    $x = $Pe.Bytes
    $sb = New-Object Text.StringBuilder
    $letters = 0
    for ($i = $off; $i -lt [Math]::Min($x.Length, $off + 100); $i++) {
        $c = $x[$i]
        if ($c -eq 0) { break }
        if ($c -ge 0x80) { [void]$sb.Append('?'); continue }
        if ($c -lt 0x20 -and $c -ne 9 -and $c -ne 10) { return $null }
        if (($c -ge 0x41 -and $c -le 0x5A) -or ($c -ge 0x61 -and $c -le 0x7A)) { $letters++ }
        [void]$sb.Append([char]$c)
    }
    if ($sb.Length -lt 4 -or $letters -lt 3) { return $null }
    return $sb.ToString().Replace("`n", '\n').Replace("`t", '\t')
}

# True when the bytes just before $Rva are a call instruction, so $Rva is a real return address.
function Test-CallBefore($Pe, [int64]$Rva) {
    $off = Get-FileOffset $Pe $Rva
    if ($off -lt 7) { return $false }
    $x = $Pe.Bytes
    if ($x[$off - 5] -eq 0xE8) { return $true }
    if ($x[$off - 6] -eq 0xFF -and ($x[$off - 5] -eq 0x15 -or ($x[$off - 5] -band 0xF8) -eq 0x90)) { return $true }
    if ($x[$off - 7] -eq 0xFF -and $x[$off - 6] -eq 0x94) { return $true }
    if ($x[$off - 3] -eq 0xFF -and ($x[$off - 2] -band 0xF8) -eq 0x50) { return $true }
    if ($x[$off - 4] -eq 0xFF -and $x[$off - 3] -eq 0x54) { return $true }
    if ($x[$off - 2] -eq 0xFF -and (($x[$off - 1] -band 0xF8) -eq 0xD0 -or ($x[$off - 1] -band 0xF8) -eq 0x10)) { return $true }
    if ($x[$off - 3] -eq 0xFF -and $x[$off - 2] -eq 0x14) { return $true }
    return $false
}

function Write-CodeWindow($Pe, [int64]$Rva, [int]$Before, [int]$After, [string]$Label) {
    $off = Get-FileOffset $Pe ($Rva - $Before)
    if ($off -lt 0 -or $off + $Before + $After -gt $Pe.Bytes.Length) { Note ('{0} exe+{1:X}: not in the exe file' -f $Label, $Rva); return }
    $len = $Before + $After
    Note ('{0} exe+{1:X} from -{2:X}: {3}' -f $Label, $Rva, $Before, [BitConverter]::ToString($Pe.Bytes, [int]$off, $len).Replace('-', ''))
    $seen = @{}
    for ($k = 0; $k -le $len - 4; $k++) {
        $v = U32 $Pe.Bytes ($off + $k)
        $r = $v - $Pe.Base
        if ($r -lt 0x1000 -or $r -ge $Pe.ImageSize -or $seen.ContainsKey($v)) { continue }
        $seen[$v] = $true
        $s = Get-CString $Pe $r
        if ($s) { Note ('  str {0:X8} "{1}"' -f $v, $s) }
    }
}

# --- Windows Error Reporting crash dump (minidump) ---

function Set-DumpCapture([bool]$On) {
    $hklm = [Microsoft.Win32.RegistryKey]::OpenBaseKey('LocalMachine', 'Registry64')
    try {
        if ($On) {
            $k = $hklm.CreateSubKey($DumpKey)
            $k.SetValue('DumpFolder', $DumpDir, 'ExpandString')
            $k.SetValue('DumpType', 1, 'DWord')
            $k.SetValue('DumpCount', 5, 'DWord')
            $k.Close()
        } else {
            $hklm.DeleteSubKeyTree($DumpKey, $false)
        }
    } finally { $hklm.Close() }
}

function Find-Module($Mods, [int64]$Addr) {
    foreach ($m in $Mods) { if ($Addr -ge $m.Base -and $Addr -lt $m.Base + $m.Size) { return $m } }
    return $null
}

function Format-Address($Mods, [int64]$Addr) {
    $m = Find-Module $Mods $Addr
    if ($m) { return '{0}+{1:X}' -f $m.Short, ($Addr - $m.Base) }
    return '{0:X8}' -f $Addr
}

# Reads the crash from a minidump and returns the crash address and the return addresses found on the stack.
function Read-CrashDump([string]$Path, $Pe) {
    $b = [IO.File]::ReadAllBytes($Path)
    if ($b.Length -lt 32 -or [Text.Encoding]::ASCII.GetString($b, 0, 4) -ne 'MDMP') { Note 'dump: not a minidump'; return $null }
    $streams = @{}
    $dir = U32 $b 12
    for ($i = 0; $i -lt (U32 $b 8); $i++) { $o = $dir + 12 * $i; $streams[[int](U32 $b $o)] = U32 $b ($o + 8) }
    foreach ($need in 3, 4, 6) { if (-not $streams.ContainsKey($need)) { Note "dump: stream $need missing"; return $null } }
    $arch = if ($streams.ContainsKey(7)) { [int][BitConverter]::ToUInt16($b, [int]$streams[7]) } else { -1 }

    $mods = @()
    $m = $streams[4]
    for ($i = 0; $i -lt (U32 $b $m); $i++) {
        $o = $m + 4 + 108 * $i
        $nameRva = U32 $b ($o + 20)
        $name = ([Text.Encoding]::Unicode.GetString($b, [int]$nameRva + 4, [int](U32 $b $nameRva)) -split '[\\/]')[-1]
        $short = if ($name -ieq "$ServerName.exe") { 'exe' } else { $name }
        $mods += [pscustomobject]@{ Short = $short; Base = [int64][BitConverter]::ToUInt64($b, [int]$o); Size = U32 $b ($o + 8) }
    }
    $exeMod = $mods | Where-Object { $_.Short -eq 'exe' } | Select-Object -First 1

    $e = $streams[6]
    $tid = U32 $b $e
    $code = U32 $b ($e + 8)
    $addr = [int64][BitConverter]::ToUInt64($b, [int]($e + 24))
    $kind = @{ 0 = 'reading'; 1 = 'writing'; 8 = 'running' }[[int](U32 $b ($e + 40))]
    $target = U32 $b ($e + 48)
    Note ('dump: arch {0}, code {1:X8} at {2}, {3} address {4:X8}' -f $arch, $code, (Format-Address $mods $addr), $kind, $target)
    $result = [pscustomobject]@{ CrashRva = $(if ($exeMod -and (Find-Module @($exeMod) $addr)) { $addr - $exeMod.Base } else { -1 }); Returns = @() }
    if ($arch -ne 0) { Note 'dump: not a 32-bit dump, so no stack'; return $result }

    $ctx = U32 $b ($e + 164)
    $r = @{}
    foreach ($reg in @(@('edi', 0x9C), @('esi', 0xA0), @('ebx', 0xA4), @('edx', 0xA8), @('ecx', 0xAC), @('eax', 0xB0), @('ebp', 0xB4), @('eip', 0xB8), @('esp', 0xC4))) {
        $r[$reg[0]] = U32 $b ($ctx + $reg[1])
    }
    Note ('regs: eax={0:X8} ebx={1:X8} ecx={2:X8} edx={3:X8} esi={4:X8} edi={5:X8} ebp={6:X8} esp={7:X8}' -f
        $r.eax, $r.ebx, $r.ecx, $r.edx, $r.esi, $r.edi, $r.ebp, $r.esp)

    $t = $streams[3]
    $stackStart = -1
    for ($i = 0; $i -lt (U32 $b $t); $i++) {
        $o = $t + 4 + 48 * $i
        if ((U32 $b $o) -eq $tid) {
            $stackStart = [int64][BitConverter]::ToUInt64($b, [int]($o + 24)); $stackSize = U32 $b ($o + 32); $stackRva = U32 $b ($o + 36)
        }
    }
    if ($stackStart -lt 0) { Note 'dump: crashing thread not found'; return $result }
    $from = $r.esp - $stackStart
    if ($from -lt 0 -or $from -ge $stackSize) { $from = 0 }
    $to = [Math]::Min($stackSize, $from + 0x3000)

    $hits = @(); $returns = @()
    for ($o = $from; $o + 4 -le $to; $o += 4) {
        $v = U32 $b ($stackRva + $o)
        $mod = Find-Module $mods $v
        if (-not $mod) { continue }
        if ($mod.Short -eq 'exe') {
            $rva = $v - $mod.Base
            if (-not (Test-CallBefore $Pe $rva)) { continue }
            if ($returns -notcontains $rva) { $returns += $rva }
        }
        if ($hits.Count -lt 40) { $hits += Format-Address $mods $v }
    }
    Note ('stack: ' + ($hits -join ' '))

    # Text left on the stack, such as the name of the file the game was reading.
    $texts = @(); $run = New-Object Text.StringBuilder
    for ($o = $from; $o -lt $to; $o++) {
        $c = $b[$stackRva + $o]
        if ($c -ge 0x20 -and $c -le 0x7E) { [void]$run.Append([char]$c); continue }
        if ($run.Length -ge 6 -and $texts -notcontains $run.ToString()) { $texts += $run.ToString() }
        [void]$run.Clear()
    }
    Note ('stack text: ' + (($texts | Select-Object -First 30) -join ' | '))
    $result.Returns = $returns
    return $result
}

# --- GRF probe: can the Lua files the game needs at start be read from the GRFs? ---

$Latin1 = [Text.Encoding]::GetEncoding(28591)

function Read-GrfTable([string]$Path) {
    $fs = [IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite')
    try {
        $head = New-Object byte[] 46
        [void]$fs.Read($head, 0, 46)
        if ($Latin1.GetString($head, 0, 15) -ne 'Master of Magic') { throw 'not a GRF file' }
        $grf = [pscustomobject]@{ Version = U32 $head 42; Count = (U32 $head 38) - (U32 $head 34) - 7; Table = $null; Text = $null }
        if ($grf.Version -ne 0x200) { return $grf }
        $fs.Position = (U32 $head 30) + 46
        $sizes = New-Object byte[] 8
        [void]$fs.Read($sizes, 0, 8)
        $real = [int](U32 $sizes 4)
        $fs.Position = $fs.Position + 2   # skip the 2-byte zlib header
        $grf.Table = Expand-Deflate $fs $real
        $grf.Text = $Latin1.GetString($grf.Table)
        return $grf
    } finally { $fs.Dispose() }
}

function Expand-Deflate($Stream, [int]$Size) {
    $z = New-Object IO.Compression.DeflateStream($Stream, [IO.Compression.CompressionMode]::Decompress, $true)
    try {
        $out = New-Object byte[] $Size
        $got = 0
        while ($got -lt $Size) { $n = $z.Read($out, $got, $Size - $got); if ($n -le 0) { break }; $got += $n }
        if ($got -ne $Size) { throw "unpacked $got of $Size bytes" }
        return , $out
    } finally { $z.Dispose() }
}

# File entries whose path matches $Pattern (a regex piece). 0x200 entry: name, 0, packed, aligned, real size, flags, offset.
function Find-GrfEntries($Grf, [string]$Pattern, [int]$Max) {
    $rx = New-Object Text.RegularExpressions.Regex("data\\[^\x00]*?$Pattern[^\x00]*\x00", 'IgnoreCase')
    $list = @()
    foreach ($m in $rx.Matches($Grf.Text)) {
        $p = $m.Index + $m.Length
        $list += [pscustomobject]@{ Name = ($m.Value.TrimEnd([char]0) -replace '[^\x20-\x7E]', '?'); Packed = U32 $Grf.Table $p; Aligned = U32 $Grf.Table ($p + 4)
            Real = U32 $Grf.Table ($p + 8); Flags = [int]$Grf.Table[$p + 12]; Offset = U32 $Grf.Table ($p + 13) }
        if ($list.Count -ge $Max) { break }
    }
    return $list
}

function Read-GrfFile([string]$Path, $Entry) {
    if ($Entry.Flags -band 6) { throw 'DES-encrypted' }
    $fs = [IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite')
    try {
        $fs.Position = $Entry.Offset + 46 + 2
        return , (Expand-Deflate $fs ([int]$Entry.Real))
    } finally { $fs.Dispose() }
}

function Test-GrfLua([string]$Game) {
    $ini = Join-Path $Game 'DATA.INI'
    $names = @()
    if (Test-Path -LiteralPath $ini) { foreach ($l in Get-Content -LiteralPath $ini) { if ($l -match '^\s*\d+\s*=\s*(\S.*?)\s*$') { $names += $Matches[1] } } }
    $wanted = @(
        @('lua files\\datainfo\\npcidentity\.lu[ab]', 'jobtbl'),
        @('lua files\\datainfo\\petinfo\.lu[ab]', 'PetNameTable'),
        @('lua files\\[^\x00]*?region[^\x00]*?\.lu[ab]', 'queryRegionInfo'))
    foreach ($name in $names) {
        $path = Join-Path $Game $name
        if (-not (Test-Path -LiteralPath $path)) { Note "grf $name`: no such file"; continue }
        try { $grf = Read-GrfTable $path } catch { Note "grf $name`: cannot read ($($_.Exception.Message))"; continue }
        Note ('grf {0}: {1:N0} bytes, version 0x{2:X}, {3} files' -f $name, (Get-Item -LiteralPath $path).Length, $grf.Version, $grf.Count)
        if (-not $grf.Table) { continue }
        foreach ($w in $wanted) {
            $entries = @(Find-GrfEntries $grf $w[0] 5)
            if (-not $entries.Count) { Note "  no file like $($w[0] -replace '\\\\', '\')"; continue }
            foreach ($en in $entries) {
                try {
                    $bytes = Read-GrfFile $path $en
                    $has = if ($Latin1.GetString($bytes).Contains($w[1])) { 'yes' } else { 'no' }
                    $desc = 'starts {0}, has {1}: {2}' -f [BitConverter]::ToString($bytes, 0, [Math]::Min(5, $bytes.Length)).Replace('-', ''), $w[1], $has
                } catch { $desc = "cannot unpack: $($_.Exception.Message)" }
                Note ('  {0} ({1}/{2} bytes, flags {3}): {4}' -f $en.Name, $en.Packed, $en.Real, $en.Flags, $desc)
            }
        }
        $grf = $null
        [GC]::Collect()
    }
    # Loose files the game reads before the GRFs, and which of them define what the error boxes asked for.
    foreach ($rx in 'jobtbl\s*=', 'queryRegionInfo') {
        $hits = foreach ($dir in 'System', 'SystemEN', 'data\luafiles514') {
            $d = Join-Path $Game $dir
            if (-not (Test-Path -LiteralPath $d)) { continue }
            Get-ChildItem -LiteralPath $d -Recurse -File -Include '*.lub', '*.lua' -ErrorAction SilentlyContinue |
                Where-Object { $Latin1.GetString([IO.File]::ReadAllBytes($_.FullName)) -match $rx } |
                ForEach-Object { $_.FullName.Substring($Game.Length).TrimStart('\', '/') }
        }
        Note ("loose files matching '{0}': {1}" -f $rx, $(if ($hits) { (@($hits) | Select-Object -First 10) -join ', ' } else { 'none' }))
    }
}

# --- Test runs ---

$UiState = @{ Loaded = $false; Clicks = 0 }

function Initialize-Ui {
    if (-not $UiState.Loaded) { Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes; $UiState.Loaded = $true }
}

# Records the text of each message box the game shows and presses its button (OK), like a player would.
function Close-Dialogs([int]$ProcId, $Seen, $Handles) {
    try {
        Initialize-Ui
        $ae = [System.Windows.Automation.AutomationElement]
        $scope = [System.Windows.Automation.TreeScope]
        $button = [System.Windows.Automation.ControlType]::Button
        $byPid = New-Object System.Windows.Automation.PropertyCondition($ae::ProcessIdProperty, $ProcId)
        $isButton = New-Object System.Windows.Automation.PropertyCondition($ae::ControlTypeProperty, $button)
        $clicked = $false
        foreach ($w in $ae::RootElement.FindAll($scope::Children, $byPid)) {
            if ($w.Current.ClassName -ne '#32770') { continue }
            $handle = $w.Current.NativeWindowHandle
            if (-not $Handles.Contains($handle)) {
                [void]$Handles.Add($handle)
                $texts = @($w.Current.Name)
                foreach ($el in $w.FindAll($scope::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
                    if ($el.Current.ControlType -ne $button -and $el.Current.Name) { $texts += $el.Current.Name }
                }
                $Seen.Add(($texts | Where-Object { $_ }) -join ': ')
            }
            $btn = $w.FindFirst($scope::Descendants, $isButton)
            if ($btn -and $UiState.Clicks -lt 20) {
                $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
                $UiState.Clicks++
                $clicked = $true
            }
        }
        return $clicked
    } catch { return $false }
}

function Get-WindowTitles([int]$ProcId) {
    try {
        Initialize-Ui
        $ae = [System.Windows.Automation.AutomationElement]
        $byPid = New-Object System.Windows.Automation.PropertyCondition($ae::ProcessIdProperty, $ProcId)
        $names = foreach ($w in $ae::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $byPid)) { '{0} [{1}]' -f $w.Current.Name, $w.Current.ClassName }
        return ($names -join ' | ')
    } catch { return "(windows not readable: $($_.Exception.Message))" }
}

function Stop-Game {
    Get-Process -Name $ServerName -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 800
}

# Starts the game and clicks through its message boxes until it exits, or stays quiet for $WaitSeconds.
# Returns the start time and the exit code ($null if it kept running).
function Invoke-Run([string]$Label, [string]$Game) {
    Stop-Game
    $UiState.Clicks = 0
    $seen = New-Object System.Collections.Generic.List[string]
    $handles = New-Object System.Collections.Generic.HashSet[int]
    $start = Get-Date
    $p = Start-Process -FilePath (Join-Path $Game "$ServerName.exe") -WorkingDirectory $Game -PassThru
    $null = $p.Handle
    $quiet = $start
    while (-not $p.HasExited) {
        Start-Sleep -Milliseconds 700
        if ($p.HasExited) { break }
        if (Close-Dialogs $p.Id $seen $handles) { $quiet = Get-Date }
        $now = Get-Date
        if (($now - $quiet).TotalSeconds -ge $WaitSeconds -or ($now - $start).TotalSeconds -ge 120) { break }
    }
    $secs = [Math]::Round(((Get-Date) - $start).TotalSeconds, 1)
    $msgs = if ($seen.Count) { '; messages: ' + ($seen -join ' || ') } else { '' }
    if ($p.HasExited) {
        Note ('{0}: EXITED {1:X8} after {2}s{3}' -f $Label, $p.ExitCode, $secs, $msgs)
        return [pscustomobject]@{ Start = $start; Code = $p.ExitCode }
    }
    Note ('{0}: STILL RUNNING after {1}s; windows: {2}{3}' -f $Label, $secs, (Get-WindowTitles $p.Id), $msgs)
    Stop-Game
    return [pscustomobject]@{ Start = $start; Code = $null }
}

# Runs the game once with one folder renamed away, then puts the folder back.
function Invoke-RunWithout([string]$Folder, [string]$Game) {
    $path = Join-Path $Game $Folder
    $aside = "$path.check-off"
    if (-not (Test-Path -LiteralPath $path)) { Note "without $Folder`: skipped, there is no $Folder folder"; return $null }
    try {
        Rename-Item -LiteralPath $path -NewName (Split-Path $aside -Leaf)
    } catch { Note "without $Folder`: skipped, could not rename it ($($_.Exception.Message))"; return $null }
    try { return Invoke-Run "without $Folder" $Game }
    finally { Restore-Folder $path $aside }
}

function Restore-Folder([string]$Path, [string]$Aside) {
    if (-not (Test-Path -LiteralPath $Aside)) { return }
    if (Test-Path -LiteralPath $Path) { Rename-Item -LiteralPath $Path -NewName ((Split-Path $Path -Leaf) + '.made-by-game-' + (Get-Date -Format 'yyyyMMddHHmmss')) }
    Rename-Item -LiteralPath $Aside -NewName (Split-Path $Path -Leaf)
}

function Get-EventFaultOffset([datetime]$Since) {
    $ev = Get-WinEvent -FilterHashtable @{ LogName = 'Application'; Id = 1000; StartTime = $Since } -ErrorAction SilentlyContinue |
        Where-Object { $_.Message -match "$ServerName\.exe" } | Select-Object -First 1
    if ($ev -and $ev.Message -match 'Fault offset:\s*0x([0-9a-fA-F]+)') { return [Convert]::ToInt64($Matches[1], 16) }
    return -1
}

function Get-NewDump([datetime]$Since) {
    for ($i = 0; $i -lt 30; $i++) {
        $d = Get-ChildItem -LiteralPath $DumpDir -Filter "$ServerName.exe*.dmp" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $Since } | Sort-Object LastWriteTime | Select-Object -Last 1
        if ($d) {
            Start-Sleep -Seconds 1
            if ((Get-Item -LiteralPath $d.FullName).Length -eq $d.Length -and $d.Length -gt 0) { return $d.FullName }
        }
        Start-Sleep -Milliseconds 500
    }
    return $null
}

function Invoke-Check {
    $game = Find-Game
    foreach ($f in 'data', 'SystemEN') { Restore-Folder (Join-Path $game $f) (Join-Path $game "$f.check-off") }
    $exe = Join-Path $game "$ServerName.exe"
    $info = Get-Item -LiteralPath $exe
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    Note "PRONTERA CRASH CHECK 1"
    Note ('exe: {0} bytes, {1:yyyy-MM-dd HH:mm}, sha256 {2}; game {3}; Windows {4}; admin {5}' -f $info.Length, $info.LastWriteTime,
        (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.Substring(0, 16), $game, [Environment]::OSVersion.Version, $admin)
    $counts = foreach ($f in 'data', 'System', 'SystemEN') {
        $p = Join-Path $game $f
        $n = if (Test-Path -LiteralPath $p) { @(Get-ChildItem -LiteralPath $p -Recurse -File -ErrorAction SilentlyContinue).Count } else { 'none' }
        "$f $n"
    }
    Note ('files: ' + ($counts -join ', ') + '; ini: ' + ((Get-Content -LiteralPath (Join-Path $game 'DATA.INI') -ErrorAction SilentlyContinue) -join ' '))

    New-Item -ItemType Directory -Force -Path $DumpDir | Out-Null
    $dumpOn = $false
    if ($admin) {
        try { Set-DumpCapture $true; $dumpOn = $true } catch { Note "dump: could not turn on ($($_.Exception.Message))" }
    } else { Note 'dump: skipped, PowerShell is not running as Administrator' }

    try {
        $a = Invoke-Run 'normal start' $game
        if ($null -ne $a.Code) {
            $pe = Read-Pe $exe
            $crash = $null
            $dump = if ($dumpOn) { Get-NewDump $a.Start } else { $null }
            if ($dump) { $crash = Read-CrashDump $dump $pe } elseif ($dumpOn) { Note 'dump: Windows wrote no dump' }
            $crashRva = if ($crash -and $crash.CrashRva -ge 0) { $crash.CrashRva } else { Get-EventFaultOffset $a.Start.AddSeconds(-5) }
            if ($crashRva -ge 0) {
                Write-CodeWindow $pe $crashRva 0x180 0x40 'crash'
                if ($crash) { foreach ($ret in @($crash.Returns | Select-Object -First 10)) { Write-CodeWindow $pe $ret 0x50 0x8 'ret' } }
            } else { Note 'crash: no crash address found (no dump and no Windows event)' }
            $pe = $null
            if ($dumpOn) { Set-DumpCapture $false; $dumpOn = $false }
            $b = Invoke-RunWithout 'data' $game
            if ($b -and $null -ne $b.Code) { $null = Invoke-RunWithout 'SystemEN' $game }
        } else { Note 'The game kept running, so it did not crash this time.' }
        try { Test-GrfLua $game } catch { Note "grf check failed: $($_.Exception.Message)" }
    } finally {
        if ($dumpOn) { try { Set-DumpCapture $false } catch { } }
        Stop-Game
        foreach ($f in 'data', 'SystemEN') { Restore-Folder (Join-Path $game $f) (Join-Path $game "$f.check-off") }
    }
}

if (-not $env:PRONTERA_CHECK_LIBRARY_ONLY) {
    try {
        Invoke-Check
    } catch {
        Note "ERROR: $($_.Exception.Message)"
    } finally {
        $out = Join-Path $ToolsDir 'crash-report.txt'
        New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
        Set-Content -LiteralPath $out -Value $Report -Encoding UTF8
        try { Set-Clipboard -Value ($Report -join "`r`n") } catch { }
        Write-Host ''
        Write-Host "Done. The report is in $out and copied to the clipboard." -ForegroundColor Green
        Write-Host 'Paste it (Ctrl+V) into the chat and send it.' -ForegroundColor Green
    }
}
