@echo off
cd /d "%~dp0"
node -e "if(Number(process.versions.node.split('.')[0])<24)process.exit(1)" >nul 2>&1
if errorlevel 1 (
 echo Install Node.js 24 or later from https://nodejs.org then try again.
 pause
 exit /b 1
)
start "" "http://localhost:3000"
node src/server.js
pause
