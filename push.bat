@echo off
echo ============================================
echo KSML v0.2 Git Push
echo ============================================
echo.
echo Account: blackholeinfiverse78-rgb
echo Repository: KSML-CORE-V0.2-
echo.
echo Enter your GitHub Personal Access Token
echo (Generate at: https://github.com/settings/tokens)
echo Required scope: repo
echo.
set /p TOKEN="Token: "

echo.
echo Pushing...
git push https://blackholeinfiverse78-rgb:%TOKEN%@github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-.git main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! View at: https://github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-
) else (
    echo.
    echo FAILED! Check your token.
)
pause
