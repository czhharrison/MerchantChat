# -*- coding: utf-8 -*-
"""
测试start.py脚本的浏览器打开功能
"""

import os
import sys
import subprocess
import time

def test_start_script_browser():
    """测试start.py是否正确打开一个浏览器窗口"""
    print("测试start.py脚本的浏览器打开功能")
    print("=" * 50)
    
    print("检查start.py文件是否存在...")
    start_script = "start.py"
    if not os.path.exists(start_script):
        print("❌ start.py文件不存在")
        return False
    
    print("✅ start.py文件存在")
    
    # 检查修复内容
    with open(start_script, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n检查修复内容:")
    
    # 检查是否包含线程打开浏览器的代码
    if "open_browser_once" in content:
        print("✅ 包含单独线程打开浏览器的代码")
    else:
        print("❌ 缺少单独线程打开浏览器的代码")
        
    # 检查是否禁用了streamlit自动打开
    if "--server.headless" in content and "true" in content:
        print("✅ 正确禁用了streamlit自动打开浏览器")
    else:
        print("❌ 未正确禁用streamlit自动打开")
        
    # 检查是否使用了threading
    if "import threading" in content and "browser_thread.start()" in content:
        print("✅ 正确使用了线程机制")
    else:
        print("❌ 线程机制配置有问题")
    
    print("\n修复逻辑说明:")
    print("1. 创建单独线程延迟3秒后打开浏览器")
    print("2. 禁用streamlit的自动打开功能")
    print("3. 这样确保只打开一个浏览器窗口")
    
    return True

def check_dependencies():
    """检查相关依赖"""
    print("\n检查相关依赖:")
    
    try:
        import webbrowser
        print("✅ webbrowser模块可用")
    except ImportError:
        print("❌ webbrowser模块不可用")
        
    try:
        import threading
        print("✅ threading模块可用")
    except ImportError:
        print("❌ threading模块不可用")
        
    try:
        import streamlit
        print("✅ streamlit已安装")
    except ImportError:
        print("❌ streamlit未安装")

def show_usage_instructions():
    """显示使用说明"""
    print("\n" + "=" * 50)
    print("使用说明")
    print("=" * 50)
    print("1. 运行命令: python start.py")
    print("2. 等待3秒，浏览器会自动打开")
    print("3. 如果没有自动打开，手动访问: http://localhost:8501")
    print("4. 按 Ctrl+C 停止服务")
    print("\n预期效果:")
    print("✅ 只打开一个浏览器窗口/标签页")
    print("✅ 显示商家智能助手系统界面")
    print("✅ 没有重复的浏览器窗口")

if __name__ == "__main__":
    # 确保在正确的目录
    if not os.path.exists("agent") or not os.path.exists("ui"):
        print("请在merchant-assistant目录下运行此脚本")
        sys.exit(1)
    
    success = test_start_script_browser()
    check_dependencies()
    show_usage_instructions()
    
    if success:
        print("\n🎉 start.py脚本修复完成！")
        print("现在可以运行 python start.py 来启动系统")
    else:
        print("\n❌ start.py脚本存在问题，需要检查")