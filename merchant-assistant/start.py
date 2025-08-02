# -*- coding: utf-8 -*-
"""
商家智能助手系统快速启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time


def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'langchain',
        'langchain_community', 
        'faiss',
        'streamlit',
        'jieba'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"[ERROR] {package} 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True


def build_knowledge_base():
    """构建知识库"""
    print("\n正在构建知识库...")
    try:
        result = subprocess.run([
            sys.executable, 'build_knowledge_base.py'
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("[OK] 知识库构建成功")
            return True
        else:
            print(f"[ERROR] 知识库构建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] 知识库构建出错: {e}")
        return False


def test_system():
    """测试系统功能"""
    print("\n正在测试系统功能...")
    try:
        # 简单的导入测试
        from agent.agent_executor import MerchantAssistantAgent
        from agent.tools.merchant_tools import generate_product_title
        
        # 测试工具
        result = generate_product_title.invoke({
            "product_info": "连衣裙，粉色，夏季新款",
            "style": "爆款"
        })
        
        print(f"[OK] 系统功能正常 - 示例输出: {result}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 系统测试失败: {e}")
        return False


def start_web_app():
    """启动Web应用"""
    print("\n正在启动Web应用...")
    
    # 切换到ui目录
    ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
    os.chdir(ui_dir)
    
    # 启动streamlit
    try:
        print("Streamlit正在启动...")
        print("Web界面将在浏览器中自动打开")
        print("如果没有自动打开，请手动访问: http://localhost:8501")
        print("\n按 Ctrl+C 停止服务")
        
        # 在单独线程中延迟打开浏览器（仅一次）
        def open_browser_once():
            time.sleep(3)  # 等待streamlit启动
            try:
                webbrowser.open('http://localhost:8501')
                print("✓ 浏览器已自动打开")
            except Exception as e:
                print(f"打开浏览器失败: {e}")
        
        import threading
        browser_thread = threading.Thread(target=open_browser_once)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动streamlit（禁用自动打开浏览器，避免重复）
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.headless', 'true',  # 禁用streamlit自动打开
            '--browser.gatherUsageStats', 'false'  # 禁用统计数据收集
        ])
        
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"✗ Web应用启动失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("        商家智能助手系统 - 快速启动")
    print("=" * 60)
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"[ERROR] Python版本过低: {python_version.major}.{python_version.minor}")
        print("请使用Python 3.8或更高版本")
        return
    
    print(f"[OK] Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查当前目录
    if not os.path.exists('agent') or not os.path.exists('knowledge'):
        print("[ERROR] 请在merchant-assistant目录下运行此脚本")
        return
    
    print("[OK] 当前目录正确")
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查知识库
    vector_store_path = os.path.join('knowledge', 'vector_store')
    if not os.path.exists(vector_store_path):
        print("\n知识库不存在，正在构建...")
        if not build_knowledge_base():
            return
    else:
        print("[OK] 知识库已存在")
    
    # 测试系统
    if not test_system():
        print("\n系统测试失败，但可以尝试启动Web界面")
    
    # 启动Web应用
    start_web_app()


if __name__ == "__main__":
    main()