@echo off
REM 用于排查闪退：运行已打包的 exe，结束后暂停以便看清报错
cd /d "%~dp0"
if exist "dist\ChinesePaperGenerator\ChinesePaperGenerator.exe" (
  "dist\ChinesePaperGenerator\ChinesePaperGenerator.exe"
) else (
  echo 未找到 dist\ChinesePaperGenerator\ChinesePaperGenerator.exe
  echo 请先在项目根目录执行 build_exe.bat
)
echo.
pause
