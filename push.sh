#!/bin/bash
# KSML v0.2 Push to GitHub
# Run this with: bash push.sh YOUR_GITHUB_TOKEN

if [ -z "$1" ]; then
    echo "Usage: bash push.sh YOUR_GITHUB_TOKEN"
    echo "Generate token at: https://github.com/settings/tokens"
    exit 1
fi

TOKEN=$1
git push https://blackholeinfiverse78-rgb:$TOKEN@github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-.git main

if [ $? -eq 0 ]; then
    echo "SUCCESS! View at: https://github.com/blackholeinfiverse78-rgb/KSML-CORE-V0.2-"
else
    echo "FAILED! Check your token."
fi
