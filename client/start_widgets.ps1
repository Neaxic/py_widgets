# Desktop Widget Startup Script (PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File start_widgets.ps1

param(
    [string]$Action = "start",
    [switch]$Minimized
)

# Change to script directory
Set-Location $PSScriptRoot

# Function to check if Python is available
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Python not found. Please install Python and add it to PATH." -ForegroundColor Red
        return $false
    }
}

# Function to start widgets
function Start-Widgets {
    Write-Host "Starting Desktop Widgets..." -ForegroundColor Cyan
    
    if (-not (Test-Python)) {
        Write-Host "Press any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    
    # Start the widgets
    python startup.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nAn error occurred while starting widgets." -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Function to show configuration
function Show-Config {
    Write-Host "Current Widget Configuration:" -ForegroundColor Cyan
    python startup.py config
}

# Function to edit configuration
function Edit-Config {
    Write-Host "Opening configuration editor..." -ForegroundColor Cyan
    python startup.py edit
}

# Main script logic
switch ($Action.ToLower()) {
    "start" { Start-Widgets }
    "config" { Show-Config }
    "edit" { Edit-Config }
    "help" {
        Write-Host @"
Desktop Widget Startup Script

Usage:
    .\start_widgets.ps1                 # Start all widgets
    .\start_widgets.ps1 -Action config  # Show configuration
    .\start_widgets.ps1 -Action edit    # Edit configuration
    .\start_widgets.ps1 -Action help    # Show this help

Options:
    -Minimized                          # Start minimized (future feature)

Examples:
    .\start_widgets.ps1
    .\start_widgets.ps1 -Action config
    .\start_widgets.ps1 -Action edit
"@ -ForegroundColor Yellow
    }
    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Write-Host "Use -Action help for usage information." -ForegroundColor Yellow
    }
}
