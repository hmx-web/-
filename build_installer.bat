@echo off
setlocal
cd /d %~dp0

if not exist "dist\ChinesePaperGenerator\ChinesePaperGenerator.exe" (
  echo 未找到 dist\ChinesePaperGenerator\ChinesePaperGenerator.exe
  echo 请先运行 build_exe.bat
  exit /b 1
)

set ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if not exist "%ISCC_PATH%" (
  set ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe
)
if not exist "%ISCC_PATH%" (
  echo 未找到 Inno Setup 编译器 ISCC.exe
  echo 请先安装 Inno Setup 6: https://jrsoftware.org/isinfo.php
  exit /b 1
)

"%ISCC_PATH%" installer.iss
if errorlevel 1 (
  echo 安装包构建失败。
  exit /b 1
)

echo.
echo 安装包已生成：dist_installer\ChinesePaperGeneratorSetup.exe
endlocal
