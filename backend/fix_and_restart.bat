@echo off
chcp 65001 >nul
echo ============================================================
echo 修复并重启后端服务
echo ============================================================

echo.
echo 1. 安装缺失的依赖...
pip install flask-cors

echo.
echo 2. 检查数据库连接...
python diagnose.py

echo.
echo 3. 测试API端点...
python test_api.py

echo.
echo 4. 启动后端服务...
echo    按 Ctrl+C 停止服务
echo.
python run.py

pause
