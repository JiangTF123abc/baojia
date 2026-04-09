@echo off
chcp 65001 >nul
echo ========================================
echo 确保用户表和管理员账号存在
echo ========================================
echo.

python ensure_users_table.py

echo.
echo 按任意键退出...
pause >nul
