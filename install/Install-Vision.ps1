<#
    Vision installer for Windows.

    Run it by double-clicking Install-Vision.bat, or from PowerShell:
        powershell -ExecutionPolicy Bypass -File install\Install-Vision.ps1

    It creates a private virtual environment, installs everything Vision
    needs, downloads the models, and puts a "Vision" shortcut on the
    Desktop and in the Start Menu. Nothing is installed system-wide except
    Python itself, which it will not install silently -- see below.
#>
param(
    [string]$InstallDir = "$env:LOCALAPPDATA\Vision",
    [switch]$SkipModels,
    [switch]$Gpu
)

$ErrorActionPreference = "Stop"
function Say($m){ Write-Host "  $m" }
function Head($m){ Write-Host "`n$m" -ForegroundColor Cyan }

Write-Host @"
====================================================
  VISION - personal AI assistant
====================================================
"@ -ForegroundColor Cyan

# ---- 1. Python -------------------------------------------------------------
Head "Checking Python"
$py = $null
foreach ($cand in @("py -3.11","py -3.12","py -3","python")) {
    $exe, $arg = $cand.Split(" ",2)
    try {
        $v = & $exe $arg --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $v -match "Python 3\.(1[0-9])") { $py = $cand; break }
    } catch { }
}
if (-not $py) {
    Write-Host @"
  Python 3.10 or newer is required and was not found.

  Vision does not install it silently, because putting a language runtime
  on your PATH without asking is not something an installer should do.

    1. Get it from https://www.python.org/downloads/
    2. Tick "Add python.exe to PATH" during setup
    3. Run this installer again
"@ -ForegroundColor Yellow
    Read-Host "`nPress Enter to close"
    exit 1
}
Say "using $py"

# ---- 2. Files --------------------------------------------------------------
Head "Installing to $InstallDir"
$src = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
foreach ($item in @("vision","requirements.txt","VISION.md","LICENSE")) {
    $from = Join-Path $src $item
    if (Test-Path $from) {
        Copy-Item $from -Destination $InstallDir -Recurse -Force
        Say "copied $item"
    }
}

# ---- 3. Virtual environment ------------------------------------------------
Head "Creating a private Python environment"
$venv = Join-Path $InstallDir ".venv"
$exe, $arg = $py.Split(" ",2)
if ($arg) { & $exe $arg -m venv $venv } else { & $exe -m venv $venv }
$vpy = Join-Path $venv "Scripts\python.exe"
Say "venv at $venv"

Head "Installing dependencies (a few minutes)"
& $vpy -m pip install --upgrade pip --quiet
& $vpy -m pip install -r (Join-Path $InstallDir "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Dependency install failed. Scroll up for the reason." -ForegroundColor Red
    Read-Host "`nPress Enter to close"; exit 1
}
Say "dependencies installed"

if ($Gpu) {
    Head "Rebuilding llama-cpp-python with CUDA"
    Say "this needs the CUDA Toolkit and Visual Studio Build Tools"
    $env:CMAKE_ARGS = "-DGGML_CUDA=on"
    & $vpy -m pip install llama-cpp-python --force-reinstall --no-cache-dir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  CUDA build failed. Vision still works on CPU." -ForegroundColor Yellow
    }
}

Head "Installing the browser for the browser agent (~150 MB)"
& $vpy -m playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Chromium install failed. The browser agent will say so" -ForegroundColor Yellow
    Write-Host "  until you run: $vpy -m playwright install chromium" -ForegroundColor Yellow
} else { Say "chromium installed" }

# ---- 4. Models -------------------------------------------------------------
if (-not $SkipModels) {
    Head "Downloading models (~2.9 GB, resumable)"
    Push-Location $InstallDir
    & $vpy -m vision.setup_models
    Pop-Location
} else {
    Say "skipped models -- run `"$vpy -m vision.setup_models`" later"
}

# ---- 5. Launcher -----------------------------------------------------------
Head "Creating the launcher"
# Vision.cmd, not "Vision" -- the package directory is called vision,
# and on a case-insensitive filesystem a launcher named "Vision"
# collides with it. The Linux installer hit exactly that.
$launch = Join-Path $InstallDir "Vision.cmd"
@"
@echo off
cd /d "%~dp0"
start "" http://127.0.0.1:8765
"%~dp0.venv\Scripts\python.exe" -m vision
pause
"@ | Set-Content -Encoding ASCII $launch

$ws = New-Object -ComObject WScript.Shell
foreach ($dir in @([Environment]::GetFolderPath("Desktop"),
                   (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"))) {
    $lnk = $ws.CreateShortcut((Join-Path $dir "Vision.lnk"))
    $lnk.TargetPath = $launch
    $lnk.WorkingDirectory = $InstallDir
    $lnk.Description = "Vision - personal AI assistant"
    $lnk.Save()
}
Say "shortcut on the Desktop and in the Start Menu"

# ---- 6. Verify -------------------------------------------------------------
Head "Checking the installation"
Push-Location $InstallDir
& $vpy -m vision --check
Pop-Location

Write-Host @"

====================================================
  Installed.

  Launch it from the Desktop shortcut, or run
      $launch

  Then open  http://127.0.0.1:8765

  Connect your Obsidian vault in Settings, or set
      VISION_VAULT=C:\path\to\your\vault
====================================================
"@ -ForegroundColor Green
Read-Host "Press Enter to close"
