@echo off
cd /d "d:\固定资产二维码识别系统\gudingzichan"

echo [1/4] Initializing git...
git init

echo [2/4] Adding files...
git add index.html

echo [3/4] Committing...
git commit -m "Initial commit"

echo [4/4] Pushing to GitHub...
git branch -M main
git remote add origin https://github.com/sidot33/asset-qr-system.git
git push -u origin main

echo.
echo Done! If prompted, enter your GitHub username and Personal Access Token (not password).
echo Then go to https://github.com/sidot33/asset-qr-system/settings/pages to enable GitHub Pages.
pause
