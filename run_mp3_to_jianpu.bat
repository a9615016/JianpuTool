@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

if "%~1"=="" (
  echo 用法: run_mp3_to_jianpu.bat "你的歌曲.mp3"
  pause
  exit /b 1
)

python main.py "%~1"
if errorlevel 1 (
  echo.
  echo ===== 轉換失敗 =====
  pause
  exit /b 1
)

echo.
echo ===== 轉換完成 =====
pause
