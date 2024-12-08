#!/bin/bash

# 시스템 업데이트
apt-get update && apt-get install -y wget gnupg unzip

# Google Chrome 설치
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update && apt-get install -y google-chrome-stable

# ChromeDriver 설치
CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
