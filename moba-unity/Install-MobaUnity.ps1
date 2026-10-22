# Install-MobaUnity.ps1  -  ติดตั้ง Unity และเปิดเกม "ศึกลงกา MOBA" ให้ในคำสั่งเดียว (Windows)
# ใช้งาน: เปิด PowerShell แล้ววาง
#   irm https://raw.githubusercontent.com/itpppc/SEVER-GAME-prontera/main/moba-unity/Install-MobaUnity.ps1 | iex
# ไม่ลบหรือแก้ไฟล์อื่นในเครื่อง ลงเฉพาะ Unity Hub, Unity 6 LTS และโฟลเดอร์โปรเจกต์ของเกมนี้
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Ref  = if ($env:MOBA_REF) { $env:MOBA_REF } else { 'main' }
$Repo = 'itpppc/SEVER-GAME-prontera'
$Dest = if (Test-Path 'F:\') { 'F:\ProjectAI\SuekLanka-MOBA' } else { Join-Path $env:USERPROFILE 'SuekLanka-MOBA' }
$HubExe = 'C:\Program Files\Unity Hub\Unity Hub.exe'
$EditorRoot = 'C:\Program Files\Unity\Hub\Editor'

function Say($m) { Write-Host ""; Write-Host ">> $m" -ForegroundColor Yellow }
function Ok($m)  { Write-Host "   $m" -ForegroundColor Green }

Say "1/5 ตรวจสอบ Unity Hub"
if (-not (Test-Path $HubExe)) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        winget install -e --id Unity.UnityHub --accept-package-agreements --accept-source-agreements | Out-Host
    }
    if (-not (Test-Path $HubExe)) {
        $setup = Join-Path $env:TEMP 'UnityHubSetup.exe'
        Invoke-WebRequest 'https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.exe' -OutFile $setup
        Start-Process $setup -ArgumentList '/S' -Wait
    }
}
if (-not (Test-Path $HubExe)) { throw 'ติดตั้ง Unity Hub ไม่สำเร็จ ลองโหลดเองที่ https://unity.com/download แล้วรันคำสั่งนี้อีกครั้ง' }
Ok 'พบ Unity Hub แล้ว'

Say "2/5 ตรวจสอบ Unity Editor (รุ่น 6000 = Unity 6)"
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
    } catch { Write-Host '   (ดึงรุ่นล่าสุดจากเว็บ Unity ไม่ได้ ลองถาม Unity Hub แทน)' }
    if (-not $ver) {
        $list = & $HubExe -- --headless editors -r 2>&1 | Out-String
        $m = [regex]::Match($list, '6000\.\d+\.\d+f\d+')
        if ($m.Success) { $ver = $m.Value }
    }
    if (-not $ver) { throw 'หารุ่น Unity 6 ไม่เจอ เปิด Unity Hub ติดตั้ง Unity 6 LTS เองแล้วรันคำสั่งนี้ใหม่' }
    Write-Host "   กำลังติดตั้ง Unity $ver (ไฟล์ใหญ่ราว 3-5 GB ใช้เวลาสักพัก อย่าปิดหน้าต่างนี้)"
    if ($cs) { & $HubExe -- --headless install --version $ver --changeset $cs | Out-Host }
    else     { & $HubExe -- --headless install --version $ver | Out-Host }
    $deadline = (Get-Date).AddMinutes(60)
    while (-not (Test-Path (Join-Path $EditorRoot "$ver\Editor\Unity.exe")) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 10 }
    $unity = Join-Path $EditorRoot "$ver\Editor\Unity.exe"
    if (-not (Test-Path $unity)) { throw 'Unity ยังติดตั้งไม่เสร็จ รอสักครู่แล้วรันคำสั่งเดิมอีกครั้ง' }
}
Ok "พบ Unity ที่ $unity"

Say "3/5 ดาวน์โหลดโปรเจกต์เกม"
$zip = Join-Path $env:TEMP 'suek-lanka.zip'; $tmp = Join-Path $env:TEMP 'suek-lanka-src'
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
Invoke-WebRequest "https://github.com/$Repo/archive/refs/heads/$Ref.zip" -OutFile $zip
Expand-Archive $zip -DestinationPath $tmp -Force
$src = Get-ChildItem $tmp -Directory | Select-Object -First 1
$proj = Join-Path $src.FullName 'moba-unity'
if (-not (Test-Path $proj)) { throw "ไม่พบโฟลเดอร์ moba-unity ในสาขา $Ref" }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
robocopy $proj $Dest /E /XD Library Temp Builds Logs UserSettings /NFL /NDL /NJH /NJS | Out-Null
Ok "วางโปรเจกต์ไว้ที่ $Dest"

Say "4/5 เปิดโปรเจกต์ใน Unity (ครั้งแรกใช้เวลา 2-5 นาที)"
Start-Process $unity -ArgumentList @('-projectPath', "`"$Dest`"")

Say "5/5 เหลือแค่นี้"
Write-Host '   1) ถ้า Unity ขอให้ล็อกอิน ให้ล็อกอินด้วยบัญชี Unity ID (สมัครฟรี) แล้วเลือกใบอนุญาต Personal (ฟรี)'
Write-Host '   2) รอจนหน้าจอ Unity เปิดขึ้นมาและหยุดโหลด'
Write-Host '   3) กดปุ่ม ▶ Play ตรงกลางด้านบน แล้วเลือกฮีโร่ กด "เริ่มเล่น"'
Write-Host ''
Write-Host '   ถ้ามีข้อความสีแดงใน Console ของ Unity ให้ถ่ายภาพหน้าจอส่งมาที่แชต Claude ได้เลย' -ForegroundColor Cyan
