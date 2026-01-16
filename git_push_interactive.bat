@echo off
setlocal enabledelayedexpansion

echo ============================================
echo KSML v0.2 - Git Account Selection and Push
echo ============================================
echo.

:MENU
echo Select Git Account Option:
echo.
echo 1. Use current account (Ishan Shirode - ishanshirode7679@gmail.com)
echo 2. Use different GitHub account
echo 3. View current Git configuration
echo 4. Exit
echo.
set /p CHOICE="Enter your choice (1-4): "

if "%CHOICE%"=="1" goto USE_CURRENT
if "%CHOICE%"=="2" goto USE_DIFFERENT
if "%CHOICE%"=="3" goto VIEW_CONFIG
if "%CHOICE%"=="4" goto END

echo Invalid choice. Please try again.
echo.
goto MENU

:USE_CURRENT
echo.
echo Using current account: Ishan Shirode (ishanshirode7679@gmail.com)
echo.
set USERNAME=ISHANSHIRODE01
goto PUSH

:USE_DIFFERENT
echo.
echo Configure New Git Account
echo -------------------------
set /p NEW_NAME="Enter your full name: "
set /p NEW_EMAIL="Enter your email: "
set /p USERNAME="Enter your GitHub username: "

git config user.name "%NEW_NAME%"
git config user.email "%NEW_EMAIL%"

echo.
echo Git account configured:
echo Name: %NEW_NAME%
echo Email: %NEW_EMAIL%
echo Username: %USERNAME%
echo.
goto PUSH

:VIEW_CONFIG
echo.
echo Current Git Configuration:
echo -------------------------
git config --list | findstr user
echo.
pause
goto MENU

:PUSH
echo.
echo ============================================
echo Ready to Push to GitHub
echo ============================================
echo Repository: https://github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-.git
echo Username: %USERNAME%
echo.
echo You need a Personal Access Token (PAT) to push.
echo Generate one at: https://github.com/settings/tokens
echo Required scope: repo (full control)
echo.
set /p TOKEN="Enter your GitHub Personal Access Token: "

if "%TOKEN%"=="" (
    echo ERROR: Token cannot be empty!
    pause
    goto MENU
)

echo.
echo Pushing to repository...
echo.

git push https://%USERNAME%:%TOKEN%@github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-.git main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS! KSML v0.2 pushed to GitHub
    echo ============================================
    echo.
    echo View your repository at:
    echo https://github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-
    echo.
    echo Commit: KSML v0.2 Complete - Production Ready Release
    echo Files: 30 changed, 3706 insertions, 294 deletions
    echo.
) else (
    echo.
    echo ============================================
    echo PUSH FAILED
    echo ============================================
    echo.
    echo Possible reasons:
    echo 1. Invalid token or username
    echo 2. Token doesn't have 'repo' scope
    echo 3. Repository doesn't exist or no access
    echo.
    echo Try again with correct credentials.
    echo.
    pause
    goto MENU
)

:END
echo.
echo Exiting...
endlocal
