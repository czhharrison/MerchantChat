@echo off
chcp 65001
echo ============================================
echo     商家智能助手系统 - 一键安装
echo ============================================

echo.
echo 正在检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
cd merchant-assistant
pip install -r requirements.txt

echo.
echo 正在构建知识库...  
python build_knowledge_base.py

echo.
echo 正在测试系统...
python -c "from agent.tools.merchant_tools import generate_product_title; print('系统测试通过')"

echo.
echo ============================================
echo           安装完成！
echo ============================================
echo.
echo 启动方法：
echo   方法1：cd merchant-assistant && python start.py
echo   方法2：cd merchant-assistant/ui && streamlit run streamlit_app.py
echo.
echo Web界面地址：http://localhost:8501
echo.
pause