# -*- coding: utf-8 -*-
"""
商家智能助手 Streamlit Web UI
提供用户友好的界面进行商品优化和策略建议
"""

import streamlit as st
import sys
import os
import json
from typing import Dict, Any

# 添加父目录到path以便导入agent模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_executor import MerchantAssistantAgent
from agent.tools.merchant_tools import (
    generate_product_title,
    suggest_strategy,
    estimate_ctr,
    analyze_competitor_title
)


def init_session_state():
    """初始化session state"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_model_type' not in st.session_state:
        st.session_state.current_model_type = None
    
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    
    # 初始化工具结果存储
    if 'tool_results' not in st.session_state:
        st.session_state.tool_results = {
            'title_generation': None,
            'strategy_suggestion': None,
            'ctr_evaluation': None,
            'competitor_analysis': None
        }


def main():
    st.set_page_config(
        page_title="商家智能助手",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # 标题和描述
    st.title("🛍️ 商家智能助手系统")
    st.markdown("""
    **功能概述：** 为中小电商商家提供智能化内容生成、策略推荐和效果评估服务
    
    - ✅ 智能标题生成（多风格）
    - ✅ 个性化策略推荐  
    - ✅ CTR效果评估
    - ✅ 竞品标题分析
    - ✅ 一站式解决方案
    """)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 系统配置")
        
        # 模型配置
        st.subheader("模型设置")
        model_type = st.selectbox(
            "选择模式",
            ["模拟模式", "Ollama模式"],
            help="模拟模式用于演示，Ollama模式需要本地部署大模型服务",
            key="sidebar_model_type"
        )
        
        if model_type == "Ollama模式":
            model_name = st.text_input("模型名称", value="qwen2.5:7b")
            model_url = st.text_input("服务地址", value="http://localhost:11434")
        
        # 检查是否需要重新初始化assistant
        if st.session_state.current_model_type != model_type or st.session_state.assistant is None:
            st.session_state.current_model_type = model_type
            
            # 根据选择的模式设置LLM类型
            if model_type == "Ollama模式":
                llm_type = "ollama_qwen"
                embedding_type = "sentence_transformers"
            else:
                llm_type = "mock"
                embedding_type = "mock"
            
            # 重新初始化assistant
            st.session_state.assistant = MerchantAssistantAgent(
                llm_type=llm_type,
                embedding_type=embedding_type
            )
            
            # 清除对话历史
            st.session_state.chat_history = []
            
            st.success(f"✅ 已切换到{model_type}")
        
        # 全局参数
        st.subheader("默认参数")
        default_audience = st.selectbox(
            "目标受众",
            ["通用", "年轻女性", "中年女性", "年轻男性", "中年男性", "学生"],
            index=0,
            key="sidebar_default_audience"
        )
        
        default_budget = st.selectbox(
            "预算水平", 
            ["低", "中等", "高"],
            index=1,
            key="sidebar_default_budget"
        )
    
    # 主界面标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 一站式解决方案", "🔧 单项工具测试", "💬 智能对话", "📊 分析报告"])
    
    with tab1:
        st.header("🎯 一站式商品优化解决方案")
        st.markdown("输入商品信息，获得完整的优化方案，包括标题生成、策略建议和效果评估。")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 商品信息输入
            product_info = st.text_area(
                "商品信息",
                placeholder="例如：连衣裙，粉色，夏季新款，价格129元，适合年轻女性",
                height=100,
                help="请输入商品的类型、颜色、季节、价格、目标用户等信息"
            )
            
            competitor_title = st.text_input(
                "竞品标题（可选）",
                placeholder="例如：【夏日清凉】粉色连衣裙女夏季新款显瘦气质裙子",
                help="输入竞品标题进行对比分析"
            )
        
        with col2:
            # 参数配置
            target_audience = st.selectbox(
                "目标受众",
                ["通用", "年轻女性", "中年女性", "年轻男性", "中年男性", "学生"],
                index=["通用", "年轻女性", "中年女性", "年轻男性", "中年男性", "学生"].index(default_audience),
                key="solution_target_audience"
            )
            
            budget = st.selectbox(
                "预算水平",
                ["低", "中等", "高"],
                index=["低", "中等", "高"].index(default_budget),
                key="solution_budget"
            )
            
            generate_solution = st.button("🚀 生成完整解决方案", type="primary")
        
        if generate_solution and product_info:
            with st.spinner("正在生成解决方案..."):
                solution = st.session_state.assistant.generate_complete_solution(
                    product_info=product_info,
                    competitor_title=competitor_title if competitor_title else None,
                    target_audience=target_audience,
                    budget=budget
                )
                
                # 保存解决方案到session state
                st.session_state.last_solution = solution
                
        # 显示保存的解决方案（如果存在）
        if hasattr(st.session_state, 'last_solution') and st.session_state.last_solution:
            solution = st.session_state.last_solution
            if solution["success"]:
                    # 显示结果
                    st.success("✅ 解决方案生成成功！")
                    
                    # 推荐标题
                    st.subheader("🏆 推荐标题")
                    recommended = solution["recommended_title"]
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{recommended['title']}**")
                        st.caption(f"风格：{recommended['style']}")
                    
                    with col2:
                        ctr_score = recommended['ctr_analysis']['ctr_percentage']
                        st.metric("预估CTR", ctr_score)
                    
                    with col3:
                        coverage = recommended['ctr_analysis']['coverage_rate']
                        st.metric("关键词覆盖率", f"{coverage:.1%}")
                    
                    # 所有标题对比
                    st.subheader("📝 标题候选方案")
                    
                    for i, eval_result in enumerate(solution["ctr_evaluations"]):
                        with st.expander(f"{eval_result['style']}风格 - CTR: {eval_result['ctr_analysis']['ctr_percentage']}"):
                            st.write(f"**标题：** {eval_result['title']}")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("CTR评分", eval_result['ctr_analysis']['ctr_percentage'])
                            with col2:
                                st.metric("标题长度", eval_result['ctr_analysis']['title_length'])
                            with col3:
                                st.metric("包含表情", "是" if eval_result['ctr_analysis']['has_emoji'] else "否")
                            with col4:
                                st.metric("紧急词汇", eval_result['ctr_analysis']['urgent_words_count'])
                            
                            # 优化建议
                            if eval_result['ctr_analysis']['recommendations']:
                                st.write("**优化建议：**")
                                for rec in eval_result['ctr_analysis']['recommendations']:
                                    st.write(f"• {rec}")
                    
                    # 策略建议
                    st.subheader("💡 营销策略建议")
                    st.info(solution["strategy_suggestion"])
                    
                    # 竞品分析
                    if "competitor_analysis" in solution:
                        st.subheader("🔍 竞品分析")
                        comp_analysis = solution["competitor_analysis"]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**竞品标题：**")
                            st.write(comp_analysis["competitor_title"])
                            
                            st.write("**竞品CTR分析：**")
                            comp_ctr = comp_analysis["competitor_ctr_analysis"]
                            st.write(f"预估CTR: {comp_ctr['ctr_percentage']}")
                        
                        with col2:
                            st.write("**关键词对比：**")
                            if comp_analysis["common_keywords"]:
                                st.write(f"共同关键词: {', '.join(comp_analysis['common_keywords'])}")
                            if comp_analysis["competitor_unique_keywords"]:
                                st.write(f"竞品独有: {', '.join(comp_analysis['competitor_unique_keywords'][:3])}")
                            if comp_analysis["our_unique_keywords"]:
                                st.write(f"我们独有: {', '.join(comp_analysis['our_unique_keywords'][:3])}")
                        
                        st.write("**差异化建议：**")
                        for suggestion in comp_analysis["differentiation_suggestions"]:
                            st.write(f"• {suggestion}")
            else:
                st.error(f"❌ 生成失败：{solution.get('error', '未知错误')}")
                
        # 清空结果按钮
        if st.button("🗑️ 清空结果"):
            if 'last_solution' in st.session_state:
                del st.session_state.last_solution
            st.rerun()
    
    with tab2:
        st.header("🔧 单项工具测试")
        st.markdown("测试各个工具模块的功能")
        
        tool_option = st.selectbox(
            "选择工具",
            ["标题生成", "策略推荐", "CTR评估", "竞品分析"],
            key="tool_option_select"
        )
        
        if tool_option == "标题生成":
            st.subheader("📝 标题生成工具")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                product_input = st.text_area("商品信息", height=100)
            with col2:
                title_style = st.selectbox("标题风格", ["爆款", "简约", "高端"], key="title_style_select")
                title_audience = st.selectbox("目标受众", ["年轻女性", "中年女性", "年轻男性", "学生", "通用"], key="title_audience_select")
                generate_title = st.button("生成标题")
            
            if generate_title and product_input:
                # 确保Assistant已初始化，使LLM实例可用
                if st.session_state.assistant is None:
                    st.error("请先在侧边栏选择模式初始化系统")
                else:
                    with st.spinner("正在生成标题..."):
                        result = generate_product_title.invoke({
                            "product_info": product_input,
                            "style": title_style,
                            "target_audience": title_audience
                        })
                    
                    # 保存结果到session state
                    st.session_state.tool_results['title_generation'] = {
                        'result': result,
                        'style': title_style,
                        'audience': title_audience,
                        'product_info': product_input
                    }
            
            # 显示保存的结果（如果存在）
            if st.session_state.tool_results['title_generation']:
                saved_result = st.session_state.tool_results['title_generation']
                st.success(f"生成的标题：**{saved_result['result']}**")
                st.info(f"风格：{saved_result['style']} | 受众：{saved_result['audience']}")
                st.caption(f"商品信息：{saved_result['product_info'][:50]}...")
                
                # 清除结果按钮
                if st.button("🗑️ 清除标题结果"):
                    st.session_state.tool_results['title_generation'] = None
                    st.rerun()
        
        elif tool_option == "策略推荐":
            st.subheader("💡 策略推荐工具")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                product_type = st.selectbox("商品类型", ["服装", "数码", "美妆", "家居", "食品"], key="strategy_product_type")
            with col2:
                audience = st.selectbox("目标受众", ["通用", "年轻女性", "中年女性", "年轻男性", "学生"], key="strategy_audience")
            with col3:
                budget_level = st.selectbox("预算", ["低", "中等", "高"], key="strategy_budget")
            
            strategy_product_info = st.text_area("商品详细信息（可选）", height=80, key="strategy_product_info")
            
            if st.button("获取策略建议"):
                # 确保Assistant已初始化，使LLM实例可用
                if st.session_state.assistant is None:
                    st.error("请先在侧边栏选择模式初始化系统")
                else:
                    with st.spinner("正在生成策略..."):
                        result = suggest_strategy.invoke({
                            "product_type": product_type,
                            "target_audience": audience,
                            "budget": budget_level,
                            "product_info": strategy_product_info or f"{product_type}商品"
                        })
                    
                    # 保存结果到session state
                    st.session_state.tool_results['strategy_suggestion'] = {
                        'result': result,
                        'product_type': product_type,
                        'audience': audience,
                        'budget': budget_level,
                        'product_info': strategy_product_info or f"{product_type}商品"
                    }
            
            # 显示保存的结果（如果存在）
            if st.session_state.tool_results['strategy_suggestion']:
                saved_result = st.session_state.tool_results['strategy_suggestion']
                st.markdown(saved_result['result'])
                st.caption(f"商品类型：{saved_result['product_type']} | 受众：{saved_result['audience']} | 预算：{saved_result['budget']}")
                
                # 清除结果按钮
                if st.button("🗑️ 清除策略结果"):
                    st.session_state.tool_results['strategy_suggestion'] = None
                    st.rerun()
        
        elif tool_option == "CTR评估":
            st.subheader("📊 CTR评估工具")
            
            title_input = st.text_input("商品标题")
            keywords_input = st.text_input("关键词（用逗号分隔）", placeholder="连衣裙,夏季,粉色")
            
            if st.button("评估CTR") and title_input and keywords_input:
                keywords = [k.strip() for k in keywords_input.split(",")]
                result = estimate_ctr.invoke({
                    "title": title_input,
                    "keywords": keywords
                })
                
                # 保存结果到session state
                st.session_state.tool_results['ctr_evaluation'] = {
                    'result': result,
                    'title': title_input,
                    'keywords': keywords_input
                }
            
            # 显示保存的结果（如果存在）
            if st.session_state.tool_results['ctr_evaluation']:
                saved_result = st.session_state.tool_results['ctr_evaluation']
                result = saved_result['result']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CTR评分", result["ctr_percentage"])
                with col2:
                    st.metric("关键词覆盖率", f"{result['coverage_rate']:.1%}")
                with col3:
                    st.metric("标题长度", result["title_length"])
                
                st.write("**优化建议：**")
                for rec in result["recommendations"]:
                    st.write(f"• {rec}")
                
                st.caption(f"标题：{saved_result['title']} | 关键词：{saved_result['keywords']}")
                
                # 清除结果按钮
                if st.button("🗑️ 清除CTR结果"):
                    st.session_state.tool_results['ctr_evaluation'] = None
                    st.rerun()
        
        elif tool_option == "竞品分析":
            st.subheader("🔍 竞品分析工具")
            
            competitor_input = st.text_input("竞品标题")
            our_keywords_input = st.text_input("我们的关键词（用逗号分隔）")
            
            if st.button("分析竞品") and competitor_input and our_keywords_input:
                our_keywords = [k.strip() for k in our_keywords_input.split(",")]
                result = analyze_competitor_title.invoke({
                    "competitor_title": competitor_input,
                    "our_keywords": our_keywords
                })
                
                # 保存结果到session state
                st.session_state.tool_results['competitor_analysis'] = {
                    'result': result,
                    'competitor_title': competitor_input,
                    'our_keywords': our_keywords_input
                }
            
            # 显示保存的结果（如果存在）
            if st.session_state.tool_results['competitor_analysis']:
                saved_result = st.session_state.tool_results['competitor_analysis']
                result = saved_result['result']
                
                st.write(f"**竞品标题：** {result['competitor_title']}")
                st.write(f"**竞品CTR：** {result['competitor_ctr_analysis']['ctr_percentage']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if result["common_keywords"]:
                        st.write(f"**共同关键词：** {', '.join(result['common_keywords'])}")
                    if result["competitor_unique_keywords"]:
                        st.write(f"**竞品独有：** {', '.join(result['competitor_unique_keywords'][:3])}")
                
                with col2:
                    if result["our_unique_keywords"]:
                        st.write(f"**我们独有：** {', '.join(result['our_unique_keywords'][:3])}")
                
                st.write("**差异化建议：**")
                for suggestion in result["differentiation_suggestions"]:
                    st.write(f"• {suggestion}")
                
                # 显示详细分析（如果存在）
                if "detailed_analysis" in result and result["detailed_analysis"] and result["detailed_analysis"] != "未能生成详细分析，请查看LLM连接状态":
                    st.subheader("📊 深度分析报告")
                    st.markdown(result["detailed_analysis"])
                    st.caption("⚡ 由Ollama LLM生成的专业分析")
                elif "detailed_analysis" in result:
                    st.info("💡 提示：切换到Ollama模式可获得LLM生成的深度分析报告")
                
                st.caption(f"竞品标题：{saved_result['competitor_title']} | 我们的关键词：{saved_result['our_keywords']}")
                
                # 清除结果按钮
                if st.button("🗑️ 清除竞品分析结果"):
                    st.session_state.tool_results['competitor_analysis'] = None
                    st.rerun()
    
    with tab3:
        st.header("💬 智能对话助手")
        st.markdown("与AI助手进行自然语言对话，获得个性化建议")
        
        # 显示对话历史
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # 用户输入
        if prompt := st.chat_input("请输入您的问题..."):
            # 添加用户消息到历史
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # 获取AI回复
            with st.spinner("思考中..."):
                response = st.session_state.assistant.process_request(prompt)
                
                if response["success"]:
                    # 添加助手回复到历史
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response["response"]
                    })
                else:
                    # 添加错误信息到历史
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"处理失败: {response['error']}"
                    })
            
            # 重新运行以显示更新的对话历史
            st.rerun()
        
        # 清除对话历史
        if st.button("🗑️ 清除对话历史"):
            st.session_state.chat_history = []
            st.session_state.assistant.memory.clear()
            st.rerun()
    
    with tab4:
        st.header("📊 系统分析报告")
        st.markdown("查看系统功能演示和分析报告")
        
        # 功能演示
        st.subheader("🎬 功能演示")
        
        demo_data = {
            "商品信息": "连衣裙，粉色，夏季新款，价格129元，适合年轻女性",
            "竞品标题": "【夏日清凉】粉色连衣裙女夏季新款显瘦气质裙子"
        }
        
        if st.button("🎯 运行演示"):
            with st.spinner("正在运行演示..."):
                solution = st.session_state.assistant.generate_complete_solution(
                    product_info=demo_data["商品信息"],
                    competitor_title=demo_data["竞品标题"],
                    target_audience="年轻女性",
                    budget="中等"
                )
                
                st.json(solution)
        
        # 系统状态
        st.subheader("⚙️ 系统状态")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("可用工具数", len(st.session_state.assistant.tools))
        with col2:
            st.metric("对话轮次", len(st.session_state.chat_history))
        with col3:
            st.metric("系统状态", "正常运行")


if __name__ == "__main__":
    main()