@echo off

REM 设置 Python 环境变量
echo Setting FLASK_APP environment variable
set FLASK_APP=app.py

REM 安装 Python 依赖
echo Installing Python dependencies
pip install -r requirements.txt

REM 运行 Flask 应用
echo Running Flask application
flask run
