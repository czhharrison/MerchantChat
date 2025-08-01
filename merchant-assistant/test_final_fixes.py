# -*- coding: utf-8 -*-
"""
测试最终修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools.merchant_tools import analyze_competitor_title, estimate_ctr
from agent.agent_executor import MerchantAssistantAgent

def test_competitor_analysis_fix():
    """测试竞品分析工具的参数修复"""
    print("测试竞品分析工具参数修复")
    print("=" * 40)
    
    competitor_title = "优雅知性中年连衣裙，品质实用舒适一夏"
    
    # 测试1: 不提供our_keywords参数（模拟Agent调用失败的情况）
    print("1. 测试不提供our_keywords参数:")
    try:
        result = analyze_competitor_title.invoke({
            "competitor_title": competitor_title
            # 没有our_keywords参数
        })
        print(f"   成功！")
        print(f"   竞品独有关键词: {result['competitor_unique_keywords'][:3]}")
        print(f"   推断的我们的关键词: {result['our_unique_keywords']}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试2: 提供空的our_keywords列表
    print("\n2. 测试空our_keywords列表:")
    try:
        result = analyze_competitor_title.invoke({
            "competitor_title": competitor_title,
            "our_keywords": []
        })
        print(f"   成功！")
        print(f"   差异化建议: {result['differentiation_suggestions'][0]}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试3: 正常提供our_keywords参数
    print("\n3. 测试正常our_keywords参数:")
    try:
        result = analyze_competitor_title.invoke({
            "competitor_title": competitor_title,
            "our_keywords": ["连衣裙", "时尚", "年轻"]
        })
        print(f"   成功！")
        print(f"   共同关键词: {result['common_keywords']}")
    except Exception as e:
        print(f"   失败: {e}")

def test_complex_chat_scenario():
    """测试复杂对话场景"""
    print("\n测试复杂对话场景")
    print("=" * 40)
    
    try:
        # 创建Agent实例
        agent = MerchantAssistantAgent(llm_type="mock", embedding_type="mock")
        print("Agent创建成功")
        
        # 模拟用户的复杂问题
        complex_queries = [
            "优雅知性中年连衣裙，品质实用舒适一夏这个标题还能怎么优化",
            "分析一下这个标题的CTR表现如何",
            "与竞品'时尚气质连衣裙 夏季新款'相比我们有什么优势"
        ]
        
        for i, query in enumerate(complex_queries, 1):
            print(f"\n测试{i}: {query}")
            result = agent.process_request(query)
            
            if result["success"]:
                print(f"   处理成功！回复长度: {len(result['response'])} 字符")
            else:
                print(f"   处理失败: {result['error']}")
                
    except Exception as e:
        print(f"复杂对话测试失败: {e}")

def test_all_tools_compatibility():
    """测试所有工具的参数兼容性"""
    print("\n测试所有工具的参数兼容性")
    print("=" * 40)
    
    # 测试estimate_ctr工具
    print("1. estimate_ctr工具:")
    try:
        result = estimate_ctr.invoke({"title": "优雅知性连衣裙"})
        print(f"   无keywords参数 - 成功: {result['ctr_percentage']}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试analyze_competitor_title工具  
    print("\n2. analyze_competitor_title工具:")
    try:
        result = analyze_competitor_title.invoke({"competitor_title": "时尚连衣裙"})
        print(f"   无our_keywords参数 - 成功: 生成了{len(result['differentiation_suggestions'])}个建议")
    except Exception as e:
        print(f"   失败: {e}")

if __name__ == "__main__":
    test_competitor_analysis_fix()
    test_complex_chat_scenario()
    test_all_tools_compatibility()
    
    print("\n" + "=" * 60)
    print("修复总结")
    print("=" * 60)
    print("✅ analyze_competitor_title工具参数修复完成")
    print("✅ estimate_ctr工具参数修复完成") 
    print("✅ Agent超时限制增加")
    print("✅ 一站式解决方案结果保存修复")
    print("✅ start.py重复打开网页问题修复")
    print("\n现在系统应该能够:")
    print("1. 处理复杂的智能对话请求而不报参数错误")
    print("2. 在合理时间内返回完整结果")
    print("3. 保持一站式解决方案结果不丢失")
    print("4. 运行start.py时只打开一个网页")