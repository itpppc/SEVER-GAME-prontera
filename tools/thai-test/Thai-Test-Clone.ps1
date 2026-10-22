# Thai test clone: builds a second copy of the game folder with NTFS hardlinks (almost no extra disk) and
# switches only the copy to the Thai langtype. The original game folder is never modified.
#
#   Make the clone : powershell -ExecutionPolicy Bypass -File Thai-Test-Clone.ps1
#   Delete the clone: powershell -ExecutionPolicy Bypass -File Thai-Test-Clone.ps1 -Remove
#
# Files that get edited (clientinfo.xml, sclientinfo.xml and the new ExternalSettings copies) are REAL copies.
# Never edit a hardlinked file: that would change the original as well.
param(
    [string]$Src = 'C:\Gravity\Ragnarok',
    [string]$Dst = 'C:\Gravity\Ragnarok-TH',
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'

if ($Remove) {
    if ($Dst -notlike '*-TH') { throw "Refusing to delete '$Dst': the folder name must end with -TH." }
    if (Test-Path -LiteralPath $Dst) {
        Remove-Item -LiteralPath $Dst -Recurse -Force
        Write-Host "Deleted $Dst"
    } else {
        Write-Host "Nothing to delete: $Dst does not exist."
    }
    return
}

if (-not (Test-Path -LiteralPath $Src)) { throw "Game folder not found: $Src" }
if (Test-Path -LiteralPath $Dst) { throw "$Dst already exists. Run with -Remove first." }
if ((Split-Path -Qualifier $Src) -ne (Split-Path -Qualifier $Dst)) { throw 'Source and clone must be on the same drive (hardlinks).' }

$SrcFull = (Resolve-Path -LiteralPath $Src).Path.TrimEnd('\')
$editable = @('data\clientinfo.xml', 'data\sclientinfo.xml')
$latin1 = [System.Text.Encoding]::GetEncoding(28591)

try {
    New-Item -ItemType Directory -Path $Dst | Out-Null
    $DstFull = (Resolve-Path -LiteralPath $Dst).Path.TrimEnd('\')

    Get-ChildItem -LiteralPath $SrcFull -Recurse -Directory -Force | ForEach-Object {
        $rel = $_.FullName.Substring($SrcFull.Length).TrimStart('\')
        New-Item -ItemType Directory -Path (Join-Path $DstFull $rel) -Force | Out-Null
    }

    $linked = 0
    $copied = 0
    Get-ChildItem -LiteralPath $SrcFull -Recurse -File -Force | ForEach-Object {
        $rel = $_.FullName.Substring($SrcFull.Length).TrimStart('\')
        $target = Join-Path $DstFull $rel
        if ($editable -contains $rel.ToLowerInvariant()) {
            Copy-Item -LiteralPath $_.FullName -Destination $target
            $copied++
        } else {
            New-Item -ItemType HardLink -Path $target -Target $_.FullName | Out-Null
            $linked++
        }
    }
    Write-Host "Clone built: $linked hardlinked files, $copied real copies."

    # 1) langtype 5 (Thai) in the clone only. Bytes are read and written as Latin-1 so nothing else changes.
    foreach ($n in 'clientinfo.xml', 'sclientinfo.xml') {
        $f = Join-Path $DstFull "data\$n"
        if (-not (Test-Path -LiteralPath $f)) { Write-Host "Skipped (not found): data\$n"; continue }
        $text = [System.IO.File]::ReadAllText($f, $latin1)
        $new = [regex]::Replace($text, '<langtype>\s*\d+\s*</langtype>', '<langtype>5</langtype>')
        if ($new -eq $text -and $text -notmatch '<langtype>5</langtype>') { throw "No <langtype> tag found in data\$n" }
        [System.IO.File]::WriteAllText($f, $new, $latin1)
        Write-Host "data\$n -> langtype 5"
    }

    # 2) The Thai locale looks for its own ExternalSettings file, which the Korean package does not have.
    #    Copy the player's own Korean ones under Thai names. The exact folder/file name is not confirmed, so
    #    several likely names are created and the existing service_* folders are printed for the report.
    $luaRoot = Join-Path $DstFull 'data\luafiles514\lua files'
    if (-not (Test-Path -LiteralPath $luaRoot)) {
        Write-Host "NOT FOUND: $luaRoot (lua tables are not loose files here; report this)."
    } else {
        Write-Host 'Existing service folders:'
        Get-ChildItem -LiteralPath $luaRoot -Directory | Where-Object Name -like 'service_*' | ForEach-Object {
            Write-Host ("  " + $_.Name + ': ' + ((Get-ChildItem -LiteralPath $_.FullName -File | ForEach-Object Name) -join ', '))
        }
        $kr = Join-Path $luaRoot 'service_korea'
        $made = @()
        foreach ($folder in 'service_thai', 'service_thailand') {
            $thDir = Join-Path $luaRoot $folder
            New-Item -ItemType Directory -Path $thDir -Force | Out-Null
            Get-ChildItem -LiteralPath $kr -File -Filter 'ExternalSettings_kr*.lub' | ForEach-Object {
                $thName = $_.Name -replace '^ExternalSettings_kr', 'ExternalSettings_th'
                Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $thDir $thName)
                $made += "$folder\$thName"
            }
        }
        Write-Host ('Created Thai copies: ' + ($made -join ', '))
    }

    Write-Host ''
    Write-Host "Done. Start the game from $DstFull (same exe as the normal one), log in with a test account."
    Write-Host 'Executables in the clone:'
    Get-ChildItem -LiteralPath $DstFull -File -Filter '*.exe' | ForEach-Object { Write-Host ('  ' + $_.Name) }
    Write-Host "To undo everything: Thai-Test-Clone.ps1 -Remove"
}
catch {
    Write-Host "FAILED: $($_.Exception.Message)"
    if (Test-Path -LiteralPath $Dst) { Remove-Item -LiteralPath $Dst -Recurse -Force }
    Write-Host 'The clone was deleted again. The original game folder was not touched.'
    throw
}
