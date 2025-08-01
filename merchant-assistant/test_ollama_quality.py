# -*- coding: utf-8 -*-
"""
测试Ollama模式的内容生成质量
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools.merchant_tools import (
    generate_product_title,
    suggest_strategy
)
from agent.agent_executor import MerchantAssistantAgent

def test_ollama_quality():
    """测试Ollama模式的内容生成质量"""
    print("测试Ollama模式的内容生成质量")
    print("=" * 50)
    
    # 测试数据
    product_info = "连衣裙，粉色，女性"
    
    try:
        # 初始化Ollama模式
        agent = MerchantAssistantAgent(llm_type="ollama_qwen", embedding_type="sentence_transformers")
        print("Ollama连接成功")
        
        print(f"\n测试商品: {product_info}")
        
        # 测试标题生成
        print("\n1. 标题生成测试:")
        for style in ["爆款", "简约", "高端"]:
            title = generate_product_title.invoke({
                "product_info": product_info,
                "style": style,
                "target_audience": "年轻女性"
            })
            print(f"   {style}风格: {title}")
        
        # 测试营销策略
        print("\n2. 营销策略测试:")
        strategy = suggest_strategy.invoke({
            "product_type": "服装",
            "target_audience": "年轻女性", 
            "budget": "中等",
            "product_info": product_info
        })
        
        print(f"策略长度: {len(strategy)} 字符")
        print(f"策略内容:\n{strategy}")
        
    except Exception as e:
        print(f"Ollama连接失败: {e}")
        print("请确保:")
        print("1. Ollama服务正在运行")
        print("2. qwen2.5:7b模型已下载")
        print("3. 服务地址为 http://localhost:11434")

if __name__ == "__main__":
    test_ollama_quality()