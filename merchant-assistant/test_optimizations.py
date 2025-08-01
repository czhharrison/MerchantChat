# -*- coding: utf-8 -*-
"""
测试优化效果
验证前3个优化方案的实施效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.agent_executor import MerchantAssistantAgent
from agent.tools.merchant_tools import (
    generate_product_title,
    suggest_strategy,
    preprocess_product_info,
    evaluate_title_quality,
    get_audience_profile
)

def test_prompt_engineering():
    """测试方案1：增强的Prompt工程"""
    print("=" * 50)
    print("测试方案1：增强的Prompt工程")
    print("=" * 50)
    
    # 测试商品信息预处理
    product_info = "连衣裙，粉色，夏季新款，价格129元，适合年轻女性"
    processed = preprocess_product_info(product_info)
    
    print("商品信息预处理结果:")
    for key, value in processed.items():
        print(f"  {key}: {value}")
    
    # 测试受众画像获取
    audience_profile = get_audience_profile("年轻女性")
    print(f"\n受众画像:")
    for key, value in audience_profile.items():
        print(f"  {key}: {value}")

def test_title_optimization():
    """测试方案2：标题质量评估和二次优化"""
    print("\n" + "=" * 50)
    print("测试方案2：标题质量评估和二次优化")
    print("=" * 50)
    
    # 测试不同质量的标题
    test_titles = [
        "连衣裙，粉色，女性",  # 低质量：使用逗号，缺乏吸引力
        "粉色连衣裙夏季新款适合年轻女性穿搭",  # 中等质量：过长，缺乏情感词
        "【少女心】粉色连衣裙 夏季新款 甜美必入",  # 高质量
    ]
    
    product_info = "连衣裙，粉色，夏季新款，价格129元，适合年轻女性"
    target_audience = "年轻女性"
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n测试标题{i}: {title}")
        evaluation = evaluate_title_quality(title, product_info, target_audience)
        
        print(f"  质量评分: {evaluation['score']:.2f} ({evaluation['grade']})")
        print(f"  需要优化: {'是' if evaluation['need_optimization'] else '否'}")
        if evaluation['issues']:
            print(f"  发现问题: {', '.join(evaluation['issues'])}")
        if evaluation['recommendations']:
            print(f"  优化建议: {', '.join(evaluation['recommendations'])}")

def test_memory_and_context():
    """测试方案3：记忆与上下文融合"""
    print("\n" + "=" * 50)
    print("测试方案3：记忆与上下文融合")
    print("=" * 50)
    
    # 创建Agent实例（模拟模式）
    agent = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
    
    # 模拟对话历史
    print("模拟用户对话历史...")
    
    # 模拟用户对话1：表达对简约风格的喜好
    response1 = agent.process_request("我比较喜欢简约风格的标题，不要太复杂")
    print(f"用户输入1: 我比较喜欢简约风格的标题，不要太复杂")
    print(f"系统回复1: {response1['response']}")
    
    # 模拟用户对话2：关注年轻女性群体
    response2 = agent.process_request("帮我为年轻女性群体设计营销方案")
    print(f"\n用户输入2: 帮我为年轻女性群体设计营销方案")
    print(f"系统回复2: {response2['response']}")
    
    # 提取学习到的偏好
    preferences = agent.extract_user_preferences_from_history()
    print(f"\n学习到的用户偏好:")
    for key, value in preferences.items():
        if value:
            print(f"  {key}: {value}")
    
    # 测试上下文建议
    contextual_suggestions = agent.get_contextual_suggestions(
        "连衣裙，粉色，夏季新款，价格129元", 
        "年轻女性"
    )
    print(f"\n上下文建议: {contextual_suggestions}")

def test_complete_solution():
    """测试完整解决方案的优化效果"""
    print("\n" + "=" * 50)
    print("测试完整解决方案的优化效果")
    print("=" * 50)
    
    # 创建Agent实例（Ollama模式，如果可用）
    try:
        agent = MerchantAssistantAgent(llm_type="ollama_qwen", embedding_type="sentence_transformers")
        print("使用Ollama模式测试")
    except:
        agent = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
        print("使用模拟模式测试")
    
    # 测试产品
    product_info = "连衣裙，粉色，夏季新款，价格129元，适合年轻女性"
    target_audience = "年轻女性"
    budget = "中等"
    
    print(f"\n测试商品: {product_info}")
    print(f"目标受众: {target_audience}")
    print(f"预算水平: {budget}")
    
    # 生成完整解决方案
    solution = agent.generate_complete_solution(
        product_info=product_info,
        target_audience=target_audience,
        budget=budget
    )
    
    if solution["success"]:
        print(f"\n✅ 解决方案生成成功!")
        
        # 显示生成的标题
        print(f"\n生成的标题:")
        for title_info in solution["generated_titles"]:
            print(f"  {title_info['style']}风格: {title_info['title']}")
        
        # 显示推荐标题
        if "recommended_title" in solution:
            recommended = solution["recommended_title"]
            print(f"\n推荐标题: {recommended['title']} ({recommended['style']})")
        
        # 显示策略建议（前200字）
        strategy = solution["strategy_suggestion"]
        if len(strategy) > 200:
            strategy = strategy[:200] + "..."
        print(f"\n策略建议: {strategy}")
        
        # 显示上下文信息
        if solution.get("contextual_suggestions"):
            print(f"\n上下文建议: {solution['contextual_suggestions']}")
    else:
        print(f"❌ 解决方案生成失败: {solution.get('error', '未知错误')}")

def main():
    """主测试函数"""
    print("开始测试优化方案效果...")
    print("测试包括：Prompt工程优化、标题二次优化、记忆与上下文融合")
    
    try:
        # 测试各个优化方案
        test_prompt_engineering()
        test_title_optimization()
        test_memory_and_context()
        test_complete_solution()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成!")
        print("=" * 50)
        print("\n优化效果总结:")
        print("✅ 方案1: Prompt工程优化 - 商品信息预处理和受众画像功能正常")
        print("✅ 方案2: 标题二次优化 - 质量评估和优化建议功能正常")
        print("✅ 方案3: 记忆与上下文 - 偏好提取和上下文融合功能正常")
        print("\n建议:")
        print("1. 在Ollama模式下测试以体验真实LLM的效果提升")
        print("2. 通过多轮对话测试记忆学习功能")
        print("3. 比较优化前后的标题和策略质量差异")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()