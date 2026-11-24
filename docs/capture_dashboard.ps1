$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
    $chrome = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
}

$artifactDir = "C:\Users\jaswant karun\.gemini\antigravity\brain\ccdc3978-e39e-4041-ac1a-6d43bb2834f7\screenshots"
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
New-Item -ItemType Directory -Force -Path "c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots" | Out-Null

$out1 = "c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots\dashboard_overview.png"
$out2 = "c:\Users\jaswant karun\TRUSTLENS AI\docs\screenshots\dashboard_full.png"

Write-Host "Capturing dashboard overview..."
& $chrome --headless=new --disable-gpu --window-size=1440,1100 --screenshot=$out1 "http://localhost:3000/dashboard"
Start-Sleep -Seconds 3

Write-Host "Capturing dashboard full page..."
& $chrome --headless=new --disable-gpu --window-size=1440,2600 --screenshot=$out2 "http://localhost:3000/dashboard"

Copy-Item $out1 -Destination "$artifactDir\dashboard_overview.png" -Force
Copy-Item $out2 -Destination "$artifactDir\dashboard_full.png" -Force

Write-Host "Screenshots captured successfully:"
Get-ChildItem -Path $artifactDir | Where-Object { $_.Name -like "dashboard*" } | Select-Object Name, Length, LastWriteTime
