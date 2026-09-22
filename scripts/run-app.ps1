# KASLU LAB — always clear caches before starting Streamlit (avoids stale UI/Python).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Get-Process -Name "streamlit" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

if (Test-Path ".streamlit\cache") {
    Remove-Item -Recurse -Force ".streamlit\cache"
}

Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.venv\\' } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

$userStreamlitCache = Join-Path $env:USERPROFILE ".streamlit\cache"
if (Test-Path $userStreamlitCache) {
    Remove-Item -Recurse -Force $userStreamlitCache -ErrorAction SilentlyContinue
}

& ".\.venv\Scripts\streamlit.exe" cache clear
& ".\.venv\Scripts\streamlit.exe" run app\Home.py --server.headless true
