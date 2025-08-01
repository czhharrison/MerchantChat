# -*- coding: utf-8 -*-
"""
测试智能对话修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools.merchant_tools import estimate_ctr
from agent.agent_executor import MerchantAssistantAgent

def test_ctr_fix():
    """测试CTR工具的参数修复"""
    print("测试CTR工具参数修复")
    print("=" * 40)
    
    title = "优雅知性中年连衣裙，品质实用舒适一夏"
    
    # 测试1: 不提供keywords参数（模拟Agent调用失败的情况）
    print("1. 测试不提供keywords参数:")
    try:
        result = estimate_ctr.invoke({
            "title": title
            # 没有keywords参数
        })
        print(f"   成功！CTR评分: {result['ctr_percentage']}")
        print(f"   自动提取的关键词: {result['covered_keywords']}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试2: 提供空的keywords列表
    print("\n2. 测试空keywords列表:")
    try:
        result = estimate_ctr.invoke({
            "title": title,
            "keywords": []
        })
        print(f"   成功！CTR评分: {result['ctr_percentage']}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试3: 正常提供keywords参数
    print("\n3. 测试正常keywords参数:")
    try:
        result = estimate_ctr.invoke({
            "title": title,
            "keywords": ["连衣裙", "品质", "舒适"]
        })
        print(f"   成功！CTR评分: {result['ctr_percentage']}")
    except Exception as e:
        print(f"   失败: {e}")

def test_agent_timeout():
    """测试Agent超时改进"""
    print("\n测试Agent超时改进")
    print("=" * 40)
    
    try:
        # 创建Agent实例
        agent = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
        print("Agent创建成功")
        
        # 模拟复杂对话
        user_input = "优雅知性中年连衣裙，品质实用舒适一夏这个标题还能怎么优化，根据这个标题写一份广告投送策略"
        print(f"\n测试输入: {user_input}")
        
        result = agent.process_request(user_input)
        
        if result["success"]:
            print("处理成功！")
            print(f"回复长度: {len(result['response'])} 字符")
        else:
            print(f"处理失败: {result['error']}")
            
    except Exception as e:
        print(f"Agent测试失败: {e}")

if __name__ == "__main__":
    test_ctr_fix()
    test_agent_timeout()