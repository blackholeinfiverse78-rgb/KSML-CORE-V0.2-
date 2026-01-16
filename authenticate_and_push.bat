@echo off
echo Setting up Git authentication...
git config --global credential.helper manager
git config --local user.name "blackholeinfiverse78-rgb"
git config --local user.email "blackholeinfiverse78@gmail.com"
echo.
echo Configuration complete.
echo.
echo Now attempting to push (you will be prompted for credentials)...
echo Use your GitHub username and Personal Access Token (not password)
echo.
pause
git push origin main
pause
