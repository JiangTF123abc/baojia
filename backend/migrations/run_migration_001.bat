@echo off
chcp 65001 >nul
echo ============================================================
echo 用户表邮箱字段迁移脚本
echo 任务：1.1 为 User 表添加 email 字段
echo ============================================================
echo.

cd /d "%~dp0\.."
python migrations/run_migration_001.py

echo.
pause
