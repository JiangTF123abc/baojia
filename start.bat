@echo off
chcp 65001 >nul
title 电气设备报价系统

echo 启动后端...
start "后端 Flask :5000" /D "%~dp0backend" cmd /k python run.py

echo 启动前端...
start "前端 Vite :5173" /D "%~dp0frontend" cmd /k npm run dev

timeout /t 4 /nobreak >nul

echo 打开浏览器...
start http://localhost:5173

echo.
echo 前端: http://localhost:5173
echo 后端: http://localhost:5000
echo 账号: admin / 123456
pause
