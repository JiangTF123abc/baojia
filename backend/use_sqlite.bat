@echo off
echo ============================================================
echo 切换到SQLite数据库
echo ============================================================
echo.

python switch_to_sqlite.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo 正在启动后端服务（SQLite模式）...
    echo ============================================================
    echo.
    set FLASK_ENV=testing
    python run.py
) else (
    echo.
    echo 初始化失败，请检查错误信息
    pause
)
