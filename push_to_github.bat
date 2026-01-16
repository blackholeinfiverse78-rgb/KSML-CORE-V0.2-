@echo off
echo ========================================
echo KSML v0.2 - Push to GitHub
echo ========================================
echo.
echo Repository: KSML-CORE-V0.2-
echo Account: blackholeinfiverse78-rgb
echo.
echo Enter your GitHub Personal Access Token:
echo (Generate at: https://github.com/settings/tokens)
echo.
set /p TOKEN=Token: 

if "%TOKEN%"=="" (
    echo ERROR: Token required
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push https://blackholeinfiverse78-rgb:%TOKEN%@github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-.git main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Repository updated on GitHub
    echo ========================================
    echo.
    echo View at: https://github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-
) else (
    echo.
    echo ========================================
    echo PUSH FAILED
    echo ========================================
    echo Check your token and try again.
)

pause
