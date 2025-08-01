# -*- coding: utf-8 -*-
"""
测试修复后的标题生成和营销策略效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools.merchant_tools import (
    generate_product_title,
    suggest_strategy
)
from agent.agent_executor import MerchantAssistantAgent

def test_fixes():
    """测试修复后的效果"""
    print("=" * 60)
    print("测试修复后的标题生成和营销策略效果")
    print("=" * 60)
    
    # 测试数据
    product_info = "连衣裙，粉色，女性"
    
    print(f"测试输入: {product_info}")
    print()
    
    # 1. 测试模拟模式
    print("1. 测试模拟模式:")
    agent_mock = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
    
    print("   1.1 标题生成（修复后）:")
    result_mock = generate_product_title.invoke({
        "product_info": product_info,
        "style": "爆款",
        "target_audience": "年轻女性"  # 现在包含了target_audience
    })
    print(f"       结果: {result_mock}")
    
    print("   1.2 营销策略（模拟模式）:")
    strategy_mock = suggest_strategy.invoke({
        "product_type": "服装",
        "target_audience": "年轻女性",
        "budget": "中等",
        "product_info": product_info
    })
    print(f"       结果长度: {len(strategy_mock)} 字符")
    print(f"       结果: {strategy_mock}")
    
    # 2. 测试Ollama模式（如果可用）
    print("\n2. 测试Ollama模式:")
    try:
        agent_ollama = MerchantAssistantAgent(llm_type="ollama_qwen", embedding_type="sentence_transformers")
        print("   Ollama连接成功")
        
        print("   2.1 标题生成（Ollama模式）:")
        result_ollama = generate_product_title.invoke({
            "product_info": product_info,
            "style": "爆款",
            "target_audience": "年轻女性"
        })
        print(f"       结果: {result_ollama}")
        
        print("   2.2 营销策略（Ollama模式）:")
        strategy_ollama = suggest_strategy.invoke({
            "product_type": "服装", 
            "target_audience": "年轻女性",
            "budget": "中等",
            "product_info": product_info
        })
        print(f"       结果长度: {len(strategy_ollama)} 字符")
        print(f"       结果预览: {strategy_ollama[:200]}...")
        
    except Exception as e:
        print(f"   Ollama连接失败: {e}")
    
    print("\n" + "=" * 60)
    print("修复效果对比")
    print("=" * 60)
    print("修复前问题:")
    print("1. 标题生成缺少target_audience参数，使用通用模板")
    print("2. 生成结果: '【热销爆款】连衣裙，女性'")
    print("3. 营销策略过于简短")
    print()
    print("修复后效果:")
    print("1. 标题生成包含target_audience参数")
    print("2. 模拟模式使用优化的受众词汇库")
    print("3. Ollama模式使用LLM生成专业内容")

if __name__ == "__main__":
    test_fixes()