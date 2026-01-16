@echo off
echo Clearing old credentials...
cmdkey /delete:LegacyGeneric:target=git:https://github.com
echo.
echo Credentials cleared.
echo.
echo Now push with correct account (blackholeinfiverse78-rgb)
echo You will be prompted for username and token.
echo.
echo Token: Get from https://github.com/settings/tokens
echo.
pause
git push origin main
pause
