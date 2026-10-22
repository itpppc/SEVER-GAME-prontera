# Prontera support report: collects what is needed to find why an install or login fails, in one go.
# Read-only. It changes nothing. The report goes to C:\RO-tools\support-report.txt and to the clipboard.
# Run it in PowerShell (Run as administrator is better, not required):
#   [Net.ServicePointManager]::SecurityProtocol='Tls12'; iex (iwr -UseBasicParsing https://raw.githubusercontent.com/itpppc/SEVER-GAME-prontera/main/installer/Support-Report.ps1).Content

$ErrorActionPreference = 'Continue'
$ToolsDir = 'C:\RO-tools'
$ServerIp = '54.206.105.93'
$GoodSha  = '328F5AD1DA6F5E42732F16D942DB2C697D44728F1C27CE9AD3C57898BD04909F'
$Out = New-Object System.Collections.Generic.List[string]

function Line([string]$Text) { Write-Host $Text; $Out.Add($Text) }
function Section([string]$Title) { Line ''; Line ("=== $Title ===") }
function Try-Do([string]$Label, [scriptblock]$Block) {
    try { & $Block } catch { Line ("{0}: could not read ({1})" -f $Label, $_.Exception.Message) }
}

Line ("Prontera support report {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))

Section 'Computer'
Try-Do 'os' {
    $os = Get-CimInstance Win32_OperatingSystem
    Line ("Windows: {0} build {1}, RAM {2:N1} GB" -f $os.Caption, $os.BuildNumber, ($os.TotalVisibleMemorySize / 1MB))
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    Line ("Administrator: {0}" -f $admin)
    Line ("Code page: {0}" -f (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage').ACP)
}
Try-Do 'screens' {
    Add-Type -AssemblyName System.Windows.Forms
    Line ("Screens: {0} ({1})" -f [Windows.Forms.Screen]::AllScreens.Count, (([Windows.Forms.Screen]::AllScreens | ForEach-Object { "{0}x{1}" -f $_.Bounds.Width, $_.Bounds.Height }) -join ', '))
}

Section 'Disk'
Try-Do 'disk space' {
    Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
        Line ("{0} free {1:N1} GB of {2:N1} GB" -f $_.DeviceID, ($_.FreeSpace / 1GB), ($_.Size / 1GB))
    }
}
Try-Do 'physical disk' {
    Get-PhysicalDisk | ForEach-Object { Line ("Disk: {0} {1} health {2}, status {3}" -f $_.FriendlyName, $_.MediaType, $_.HealthStatus, $_.OperationalStatus) }
}
Try-Do 'dirty bit' { Line ("C: dirty bit: {0}" -f ((fsutil dirty query C:) -join ' ')) }
Try-Do 'disk errors' {
    $since = (Get-Date).AddDays(-14)
    $ev = @(Get-WinEvent -FilterHashtable @{ LogName = 'System'; ProviderName = 'disk', 'Ntfs', 'stornvme', 'storahci'; Level = 1, 2, 3; StartTime = $since } -ErrorAction SilentlyContinue)
    Line ("Disk/NTFS errors in the last 14 days: {0}" -f $ev.Count)
    $ev | Select-Object -First 5 | ForEach-Object { Line ("  {0} {1} id {2}" -f $_.TimeCreated.ToString('MM-dd HH:mm'), $_.ProviderName, $_.Id) }
}

Section 'Antivirus'
Try-Do 'antivirus' {
    $av = @(Get-CimInstance -Namespace 'root/SecurityCenter2' -ClassName AntiVirusProduct -ErrorAction Stop)
    foreach ($a in $av) { Line ("Antivirus: {0}" -f $a.displayName) }
    if ($av.Count -eq 0) { Line 'Antivirus: none registered' }
}
Try-Do 'defender' {
    $d = Get-MpComputerStatus -ErrorAction Stop
    Line ("Defender real-time protection: {0}, controlled folder access: {1}" -f $d.RealTimeProtectionEnabled, (Get-MpPreference).EnableControlledFolderAccess)
}

Section 'Downloaded Korean setup'
$setup = Join-Path $ToolsDir 'RAG_SETUP_220120.exe'
if (Test-Path -LiteralPath $setup) {
    Try-Do 'setup' {
        $len = (Get-Item -LiteralPath $setup).Length
        Line ("Setup file: {0} bytes (good file is 3577653728)" -f $len)
        Line 'Checking the SHA256, this takes about a minute...'
        $sha = (Get-FileHash -LiteralPath $setup -Algorithm SHA256).Hash
        Line ("SHA256: {0} -> {1}" -f $sha, $(if ($sha -eq $GoodSha) { 'MATCHES the good file' } else { 'DIFFERENT from the good file (damaged download)' }))
    }
} else {
    Line "Setup file not found at $setup"
}

Section 'Game folder'
foreach ($dir in 'C:\Gravity\Ragnarok', 'C:\RO') {
    if (Test-Path -LiteralPath $dir) {
        Try-Do $dir {
            $files = @(Get-ChildItem -LiteralPath $dir -Recurse -File -ErrorAction SilentlyContinue)
            Line ("{0}: {1} files, {2:N2} GB, Prontera.exe: {3}, data.grf: {4}" -f $dir, $files.Count, (($files | Measure-Object Length -Sum).Sum / 1GB),
                (Test-Path -LiteralPath (Join-Path $dir 'Prontera.exe')), (Test-Path -LiteralPath (Join-Path $dir 'data.grf')))
        }
    } else { Line "$dir : not found" }
}
Try-Do 'running' {
    $p = @(Get-Process | Where-Object { $_.ProcessName -match 'Prontera|Ragnarok|RAG_SETUP|setup|ISBEW|msiexec' } | Select-Object -ExpandProperty ProcessName)
    Line ("Related processes running: {0}" -f $(if ($p.Count) { $p -join ', ' } else { 'none' }))
}

Section 'Game server'
foreach ($port in 6900, 6121, 5121) {
    Try-Do "port $port" {
        $c = New-Object Net.Sockets.TcpClient
        $ok = $c.ConnectAsync($ServerIp, $port).Wait(4000)
        Line ("{0}:{1} {2}" -f $ServerIp, $port, $(if ($ok -and $c.Connected) { 'open' } else { 'NOT reachable' }))
        $c.Close()
    }
}
Try-Do 'status' {
    $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 8 -Uri "http://${ServerIp}:8090/status"
    Line ("Status API: {0}" -f $r.Content)
}

Section 'Installer log (last 60 lines)'
$log = Join-Path $ToolsDir 'install-log.txt'
if (Test-Path -LiteralPath $log) { Try-Do 'log' { Get-Content -LiteralPath $log -Tail 60 | ForEach-Object { Line $_ } } }
else { Line "No install log at $log" }

if (-not (Test-Path -LiteralPath $ToolsDir)) { New-Item -ItemType Directory -Path $ToolsDir | Out-Null }
$file = Join-Path $ToolsDir 'support-report.txt'
$Out | Set-Content -LiteralPath $file -Encoding UTF8
Try-Do 'clipboard' { Set-Clipboard -Value ($Out -join "`r`n") }
Write-Host ''
Write-Host "DONE. The report is copied to the clipboard and saved at $file" -ForegroundColor Green
Write-Host 'Paste it (Ctrl+V) into the chat and send it.'
