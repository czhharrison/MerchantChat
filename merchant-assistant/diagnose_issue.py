# -*- coding: utf-8 -*-
"""
诊断标题生成质量差的根本原因
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools.merchant_tools import (
    generate_product_title,
    suggest_strategy,
    get_llm_instance,
    set_llm_instance
)
from agent.agent_executor import MerchantAssistantAgent

def diagnose_title_generation():
    """诊断标题生成问题"""
    print("=" * 60)
    print("诊断标题生成质量差的根本原因")
    print("=" * 60)
    
    # 测试数据
    product_info = "连衣裙，粉色，女性"
    
    print(f"测试输入: {product_info}")
    print()
    
    # 1. 检查当前LLM实例状态
    print("1. 检查LLM实例状态:")
    current_llm = get_llm_instance()
    if current_llm:
        print(f"   当前LLM类型: {current_llm.__class__.__name__}")
    else:
        print("   当前LLM实例: None")
    
    # 2. 测试模拟模式
    print("\n2. 测试模拟模式:")
    agent_mock = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
    
    # 单独调用工具
    print("   2.1 直接调用generate_product_title工具:")
    result_mock = generate_product_title.invoke({
        "product_info": product_info,
        "style": "爆款",
        "target_audience": "年轻女性"
    })
    print(f"       结果: {result_mock}")
    
    # 3. 测试Ollama模式（如果可用）
    print("\n3. 测试Ollama模式:")
    try:
        agent_ollama = MerchantAssistantAgent(llm_type="ollama_qwen", embedding_type="sentence_transformers")
        print("   Ollama连接成功")
        
        print("   3.1 直接调用generate_product_title工具:")
        result_ollama = generate_product_title.invoke({
            "product_info": product_info,
            "style": "爆款", 
            "target_audience": "年轻女性"
        })
        print(f"       结果: {result_ollama}")
        
    except Exception as e:
        print(f"   Ollama连接失败: {e}")
    
    # 4. 检查Web界面调用方式
    print("\n4. 模拟Web界面的调用方式:")
    # 这是Web界面实际的调用方式（缺少target_audience!）
    result_web_style = generate_product_title.invoke({
        "product_info": product_info,
        "style": "爆款"
        # 注意：这里缺少了target_audience参数！
    })
    print(f"   Web界面调用结果: {result_web_style}")
    
    # 5. 测试营销策略
    print("\n5. 测试营销策略:")
    print("   5.1 模拟模式营销策略:")
    strategy_result = suggest_strategy.invoke({
        "product_type": "服装",
        "target_audience": "年轻女性",
        "budget": "中等",
        "product_info": product_info
    })
    print(f"       结果长度: {len(strategy_result)} 字符")
    print(f"       结果预览: {strategy_result[:100]}...")
    
    print("\n" + "=" * 60)
    print("问题诊断结果")
    print("=" * 60)
    print("主要问题:")
    print("1. Web界面调用generate_product_title时缺少target_audience参数")
    print("2. 缺少target_audience导致使用默认值'通用'，生成简陋标题")
    print("3. 需要修复Web界面的工具调用参数")

if __name__ == "__main__":
    diagnose_title_generation()