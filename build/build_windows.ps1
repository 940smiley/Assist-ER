Param(
  [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"
Write-Host "Building Assist-ER Pro GUI EXE and installer artifacts..."
Push-Location gui
neu build --release
Pop-Location

New-Item -ItemType Directory -Path dist -Force | Out-Null
Copy-Item gui/dist/* dist/ -Recurse -Force

Write-Host "Creating MSIX package placeholder metadata..."
Copy-Item build/msix/AppxManifest.xml dist/AppxManifest.xml -Force
Copy-Item gui/assets/icon-placeholder.txt dist/icon-placeholder.txt -Force

Write-Host "Signing placeholder: integrate signtool in CI/release pipeline"
Write-Host "Build complete. Artifacts in ./dist"
