param(
    [string]$Python = "python",
    [switch]$GuiCheck,
    [switch]$Launch
)

$ErrorActionPreference = "Stop"
Push-Location -LiteralPath $PSScriptRoot
try {
    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        & $Python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
    }
    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    & $venvPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Core tests failed." }
    & $venvPython -m compileall -q main.py src scripts
    if ($LASTEXITCODE -ne 0) { throw "Syntax check failed." }
    $checkArgs = @("scripts/check_install.py")
    if ($GuiCheck) { $checkArgs += "--gui" }
    & $venvPython @checkArgs
    if ($LASTEXITCODE -ne 0) { throw "Installation check failed." }
    Write-Host 'Installed. Run: .\.venv\Scripts\python.exe main.py'
    if ($Launch) {
        & $venvPython main.py
        if ($LASTEXITCODE -ne 0) { throw "Application exited with an error." }
    }
} finally {
    Pop-Location
}
