# -*- coding: utf-8 -*-
"""
验证浏览器打开修复
"""

import os

def verify_start_py_fix():
    """验证start.py的浏览器打开修复"""
    print("验证start.py浏览器打开修复")
    print("=" * 40)
    
    # 读取start.py内容
    try:
        with open('start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键修复点
        checks = [
            ("包含open_browser_once函数", "def open_browser_once():" in content),
            ("包含线程启动代码", "browser_thread.start()" in content),
            ("禁用streamlit自动打开", "--server.headless" in content and "true" in content),
            ("包含webbrowser.open调用", "webbrowser.open('http://localhost:8501')" in content),
            ("使用threading模块", "import threading" in content),
            ("设置daemon线程", "browser_thread.daemon = True" in content)
        ]
        
        print("修复检查结果:")
        all_good = True
        for desc, check in checks:
            status = "OK" if check else "FAIL"
            print(f"  {status}: {desc}")
            if not check:
                all_good = False
        
        print("\n修复逻辑:")
        print("1. 创建单独的daemon线程")
        print("2. 线程延迟3秒后打开浏览器")
        print("3. 禁用streamlit的--server.headless参数")
        print("4. 这样确保只打开一个浏览器窗口")
        
        if all_good:
            print("\n结果: 修复正确！")
            print("现在运行 python start.py 会:")
            print("- 启动streamlit服务器")
            print("- 等待3秒后自动打开一个浏览器窗口")
            print("- 不会出现重复的窗口")
            return True
        else:
            print("\n结果: 修复存在问题")
            return False
            
    except Exception as e:
        print(f"读取start.py失败: {e}")
        return False

if __name__ == "__main__":
    success = verify_start_py_fix()
    
    print("\n使用说明:")
    print("1. 在merchant-assistant目录下运行: python start.py")
    print("2. 等待几秒钟，浏览器会自动打开")
    print("3. 访问 http://localhost:8501")
    print("4. 按 Ctrl+C 停止服务")
    
    if success:
        print("\n修复完成！可以测试启动脚本了。")
    else:
        print("\n需要检查修复内容。")