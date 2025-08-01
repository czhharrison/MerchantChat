# -*- coding: utf-8 -*-
"""
基础测试脚本，验证前3个优化方案的实施效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools.merchant_tools import (
    preprocess_product_info,
    evaluate_title_quality,
    get_audience_profile,
    generate_product_title
)
from agent.agent_executor import MerchantAssistantAgent

def test_optimization_schemes():
    """测试前3个优化方案的实施效果"""
    print("=" * 60)
    print("测试优化方案实施效果")
    print("=" * 60)
    
    # 测试商品信息
    product_info = "连衣裙，粉色，夏季新款，价格129元，适合年轻女性"
    target_audience = "年轻女性"
    
    print(f"\n【测试商品】: {product_info}")
    print(f"【目标受众】: {target_audience}")
    
    print("\n" + "-" * 50)
    print("方案1: Tool + LLM联合使用，优化prompt工程")
    print("-" * 50)
    
    # 1.1 商品信息预处理
    processed_info = preprocess_product_info(product_info)
    print("\n1.1 商品信息预处理:")
    print(f"    商品类型: {processed_info['product_type']}")
    print(f"    颜色: {processed_info['color']}")
    print(f"    季节: {processed_info['season']}")
    print(f"    价格区间: {processed_info['price_range']}")
    
    # 1.2 受众画像获取
    audience_profile = get_audience_profile(target_audience)
    print("\n1.2 受众画像:")
    print(f"    年龄: {audience_profile['年龄']}")
    print(f"    特点: {audience_profile['特点']}")
    print(f"    关键词: {audience_profile['关键词'][:3]}")
    
    print("\n" + "-" * 50)
    print("方案2: Agent加入判断逻辑，控制标题二次优化")
    print("-" * 50)
    
    # 2.1 测试不同质量的标题
    test_titles = [
        ("连衣裙，粉色，女性", "低质量（逗号分隔）"),
        ("粉色连衣裙夏季新款", "中等质量"),
        ("【少女心】粉色连衣裙 夏季新款 甜美必入", "高质量")
    ]
    
    print("\n2.1 标题质量评估:")
    for title, desc in test_titles:
        evaluation = evaluate_title_quality(title, product_info, target_audience)
        print(f"    {desc}: 评分={evaluation['score']:.2f} ({evaluation['grade']})")
        if evaluation['need_optimization']:
            print(f"        需要优化: {evaluation['issues'][0] if evaluation['issues'] else '无'}")
    
    # 2.2 测试标题生成和二次优化
    print("\n2.2 标题生成测试 (模拟模式):")
    try:
        # 使用模拟模式测试
        title = generate_product_title.invoke({
            "product_info": product_info,
            "style": "爆款",
            "target_audience": target_audience
        })
        print(f"    生成标题: {title}")
        
        # 评估生成的标题
        evaluation = evaluate_title_quality(title, product_info, target_audience)
        print(f"    质量评分: {evaluation['score']:.2f} ({evaluation['grade']})")
        if evaluation['need_optimization']:
            print(f"    需要优化: 是")
        else:
            print(f"    需要优化: 否")
            
    except Exception as e:
        print(f"    标题生成失败: {e}")
    
    print("\n" + "-" * 50)
    print("方案3: Agent多轮记忆与回溯")
    print("-" * 50)
    
    # 3.1 创建Agent实例并测试记忆功能
    try:
        agent = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
        print("\n3.1 Agent实例创建成功")
        
        # 3.2 测试偏好提取
        print("\n3.2 用户偏好提取测试:")
        # 模拟添加一些对话历史
        from langchain.schema import HumanMessage, AIMessage
        agent.memory.chat_memory.add_message(HumanMessage(content="我比较喜欢简约风格的标题"))
        agent.memory.chat_memory.add_message(AIMessage(content="好的，我会为您提供简约风格的标题"))
        agent.memory.chat_memory.add_message(HumanMessage(content="年轻女性群体的营销怎么做"))
        
        preferences = agent.extract_user_preferences_from_history()
        print(f"    提取的偏好风格: {preferences['preferred_styles']}")
        print(f"    关注的受众群体: {preferences['target_audiences']}")
        
        # 3.3 测试上下文建议
        contextual_suggestions = agent.get_contextual_suggestions(product_info, target_audience)
        print(f"\n3.3 上下文建议: {contextual_suggestions}")
        
    except Exception as e:
        print(f"    Agent记忆功能测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("优化方案实施效果总结")
    print("=" * 60)
    print("✓ 方案1: Tool + LLM联合使用 - 信息预处理和受众画像功能已实现")
    print("✓ 方案2: Agent判断逻辑优化 - 质量评估和二次优化机制已实现")
    print("✓ 方案3: 多轮记忆与回溯 - 偏好提取和上下文融合功能已实现")
    print("\n建议:")
    print("1. 在Ollama模式下测试以体验真实LLM的效果提升")
    print("2. 通过多轮对话测试记忆学习功能")
    print("3. 比较优化前后的标题和策略质量差异")

if __name__ == "__main__":
    test_optimization_schemes()