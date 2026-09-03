# Record every screen in the game and pull one frame out of each, so the visuals
# can be reviewed without opening the editor.
#
# Frames land in scripts/_shots/<name>.png and the engine log in <name>.log.
# Pass -Frame to move the sampling point later (levels animate in over ~1s).
#
# Usage: powershell -File scripts/capture.ps1 [-Frame 40] [-Only level]
param(
    [int]$Frame = 40,
    [string]$Only = "",
    [switch]$SkipImport
)

$godot = "C:\Users\jakkr\Downloads\Godot_v4.7-stable_win64.exe\Godot_v4.7-stable_win64_console.exe"
$root = Split-Path -Parent $PSScriptRoot
$shots = Join-Path $PSScriptRoot "_shots"
New-Item -ItemType Directory -Force -Path $shots | Out-Null

# A freshly generated PNG has no .import file yet, and a theme that references
# one fails to load whole - every control silently falls back to Godot's default
# grey skin. Import first so a review never shows that instead of the real UI.
if (-not $SkipImport) {
    Write-Output "importing"
    & $godot --headless --path $root --import > (Join-Path $shots "import.log") 2>&1
}

$screens = [ordered]@{
    menu      = "res://Scenes/Levels/menu.tscn"
    options   = "res://Scenes/Levels/options.tscn"
    credit    = "res://Scenes/Levels/credit.tscn"
    game_over = "res://Scenes/Levels/game_over.tscn"
    game_win  = "res://Scenes/Levels/game_win.tscn"
}
foreach ($lv in 1..6) {
    $screens["level_{0:d2}" -f $lv] = "res://Scenes/Levels/level_{0:d2}.tscn" -f $lv
}

foreach ($name in $screens.Keys) {
    if ($Only -ne "" -and $name -notlike "*$Only*") { continue }
    $avi = Join-Path $shots "$name.avi"
    $png = Join-Path $shots "$name.png"
    $log = Join-Path $shots "$name.log"
    Write-Output "recording $name"
    & $godot --path $root $screens[$name] --write-movie $avi `
        --fixed-fps 30 --quit-after ($Frame + 5) --resolution 1280x720 > $log 2>&1
    Select-String -Path $log -Pattern 'ERROR' | ForEach-Object { "  " + $_.Line.Trim() }
    ffmpeg -y -loglevel error -i $avi -vf "select=eq(n\,$Frame)" -vframes 1 $png
    Remove-Item $avi -ErrorAction SilentlyContinue
}
Write-Output "done"
