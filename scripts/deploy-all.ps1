# Full deploy helper: GitHub push + reminders for Streamlit/Render + Vercel landing.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "=== 1. GitHub push ===" -ForegroundColor Cyan
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Git push failed — fix network/VPN, then run: git push -u origin main"
}

Write-Host "`n=== 2. Streamlit app (public) ===" -ForegroundColor Cyan
Write-Host "Open https://share.streamlit.io -> New app"
Write-Host "  Repo: Huseynitsu/kaslu-lab"
Write-Host "  Main file: streamlit_app.py  (or app/Home.py)"
Write-Host "  App URL will be like: https://kaslu-lab.streamlit.app"

Write-Host "`n=== 3. Render (Docker, optional) ===" -ForegroundColor Cyan
Write-Host "Open https://dashboard.render.com -> New -> Blueprint -> select kaslu-lab repo (render.yaml)"

Write-Host "`n=== 4. Vercel landing ===" -ForegroundColor Cyan
Set-Location (Join-Path $Root "vercel-site")
& npx --yes vercel deploy --prod
Write-Host "Landing: https://vercel-site-six-rho.vercel.app (or alias in Vercel dashboard)"
