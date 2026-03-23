@echo off
setlocal
cd /d %~dp0

echo [1/3] 安装打包依赖...
python -m pip install -U pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

echo [2/3] 清理旧产物...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/3] 打包 exe...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --console ^
  --name ChinesePaperGenerator ^
  --onedir ^
  --add-data "web_app.py;." ^
  --add-data "src;src" ^
  --collect-all streamlit ^
  --collect-all altair ^
  --collect-all httpx ^
  --hidden-import streamlit ^
  --hidden-import streamlit.web.cli ^
  --hidden-import httpx ^
  --hidden-import httpcore ^
  --hidden-import h11 ^
  --hidden-import anyio ^
  --hidden-import certifi ^
  --hidden-import idna ^
  --hidden-import sniffio ^
  --hidden-import openai ^
  --hidden-import anthropic ^
  --hidden-import pydantic ^
  --hidden-import pydantic_core ^
  --hidden-import yaml ^
  --hidden-import docx ^
  --hidden-import reportlab ^
  --hidden-import PIL ^
  app_launcher.py

if errorlevel 1 (
  echo 打包失败。
  exit /b 1
)

echo.
echo 打包完成：dist\ChinesePaperGenerator\
echo 启动文件：dist\ChinesePaperGenerator\ChinesePaperGenerator.exe
endlocal
