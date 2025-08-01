# -*- coding: utf-8 -*-
"""
商家智能助手Agent执行器
集成工具调用、多轮对话和策略决策逻辑
"""

from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.react.base import DocstoreExplorer
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

from .tools.merchant_tools import (
    generate_product_title,
    suggest_strategy, 
    estimate_ctr,
    analyze_competitor_title,
    set_llm_instance,
    preprocess_product_info,
    get_audience_profile
)


class MerchantAssistantAgent:
    """商家智能助手Agent类"""
    
    def __init__(self, llm_type: str = None, embedding_type: str = None):
        """
        初始化商家助手Agent
        
        Args:
            llm_type: LLM类型 (mock, ollama_qwen, ollama_qwen_large)
            embedding_type: Embedding类型 (mock, sentence_transformers, sentence_transformers_large)
        """
        self.llm_type = llm_type or Config.DEFAULT_LLM
        self.embedding_type = embedding_type or Config.DEFAULT_EMBEDDING
        self.llm_config = Config.get_llm_config(self.llm_type)
        self.embedding_config = Config.get_embedding_config(self.embedding_type)
        
        # 初始化LLM
        self.llm = self._init_llm()
        
        # 设置LLM实例到工具中
        set_llm_instance(self.llm)
        
        # 初始化工具
        self.tools = self._init_tools()
        
        # 初始化增强记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000  # 控制记忆长度
        )
        
        # 用户偏好记忆
        self.user_preferences = {
            "preferred_styles": [],
            "target_audiences": [],
            "feedback_history": [],
            "successful_titles": [],
            "successful_strategies": []
        }
        
        # 初始化Agent
        self.agent_executor = self._init_agent()
    
    def _init_llm(self):
        """初始化大语言模型"""
        if self.llm_config["type"] == "mock":
            print(f"使用模拟LLM模式 - {self.llm_config['description']}")
            return MockLLM()
        
        elif self.llm_config["type"] == "ollama":
            try:
                print(f"尝试连接Ollama模型: {self.llm_config['model_name']}")
                llm = Ollama(
                    model=self.llm_config["model_name"],
                    base_url=self.llm_config["base_url"],
                    temperature=self.llm_config.get("temperature", 0.7)
                )
                # 测试连接
                test_response = llm.invoke("你好")
                print(f"✅ Ollama模型连接成功: {self.llm_config['model_name']}")
                return llm
                
            except Exception as e:
                print(f"❌ Ollama连接失败: {e}")
                print("回退到模拟LLM模式")
                return MockLLM()
        
        else:
            print(f"未知LLM类型: {self.llm_config['type']}，使用模拟模式")
            return MockLLM()
    
    def _init_tools(self) -> List[BaseTool]:
        """初始化工具列表"""
        return [
            generate_product_title,
            suggest_strategy,
            estimate_ctr,
            analyze_competitor_title
        ]
    
    def _init_agent(self) -> AgentExecutor:
        """初始化Agent执行器"""
        
        # 定义商家助手专用Prompt模板
        prompt_template = """你是一个专业的电商运营顾问助手，帮助商家完成商品内容优化与投放策略建议。

你拥有以下工具来协助商家：
{tools}

工具名称：{tool_names}

使用以下格式进行回复：

Question: 用户的问题或需求
Thought: 分析用户需求，确定需要使用哪些工具
Action: 选择要使用的工具名称
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (可以重复 Thought/Action/Action Input/Observation 多次)
Thought: 现在我知道最终答案了
Final Answer: 给用户的最终回复，包含具体建议和解释

工作原则：
1. 始终站在商家角度，提供实用的运营建议
2. 结合数据分析给出量化的评估结果
3. 提供具体可执行的优化建议
4. 如果需要多个工具配合，按合理顺序执行

当前对话历史：
{chat_history}

用户输入：{input}

{agent_scratchpad}"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "chat_history", "agent_scratchpad"],
            partial_variables={
                "tools": self._format_tools(),
                "tool_names": self._format_tool_names()
            }
        )
        
        # 创建ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10,  # 增加迭代次数
            max_execution_time=300,  # 增加执行时间限制（5分钟）
            early_stopping_method="force",
            handle_parsing_errors=True
        )
    
    def _format_tools(self) -> str:
        """格式化工具描述"""
        tool_descriptions = []
        for tool in self.tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(tool_descriptions)
    
    def _format_tool_names(self) -> str:
        """格式化工具名称列表"""
        tool_names = [tool.name for tool in self.tools]
        return ", ".join(tool_names)
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户请求（增强版，包含学习机制）
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果字典
        """
        try:
            # 在处理前分析用户输入，提取偏好线索
            self._analyze_user_feedback(user_input)
            
            # 执行Agent
            result = self.agent_executor.invoke({"input": user_input})
            
            return {
                "success": True,
                "response": result["output"],
                "chat_history": self.memory.chat_memory.messages,
                "learned_preferences": self.extract_user_preferences_from_history()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"抱歉，处理您的请求时出现了错误：{str(e)}"
            }
    
    def _analyze_user_feedback(self, user_input: str):
        """分析用户输入中的反馈信息"""
        user_input_lower = user_input.lower()
        
        # 检测正面反馈
        positive_indicators = ["喜欢", "好", "棒", "不错", "满意", "很好"]
        negative_indicators = ["不喜欢", "不好", "不行", "差", "不满意"]
        
        # 这里可以进一步扩展学习逻辑
        # 例如：记录用户对特定风格或策略的反馈
        pass
    
    def generate_complete_solution(self, product_info: str, 
                                 competitor_title: str = None,
                                 target_audience: str = "通用",
                                 budget: str = "中等") -> Dict[str, Any]:
        """
        生成完整的商品优化解决方案（融入历史记忆）
        
        Args:
            product_info: 商品信息
            competitor_title: 竞品标题（可选）
            target_audience: 目标受众
            budget: 预算水平
            
        Returns:
            完整解决方案
        """
        
        # 提取历史偏好
        preferences = self.extract_user_preferences_from_history()
        contextual_suggestions = self.get_contextual_suggestions(product_info, target_audience)
        
        solution = {
            "product_info": product_info,
            "target_audience": target_audience,
            "budget": budget,
            "user_preferences": preferences,
            "contextual_suggestions": contextual_suggestions
        }
        
        try:
            # 1. 生成商品标题（多个版本，考虑历史偏好）
            titles = []
            
            # 基于历史偏好调整风格顺序
            base_styles = ["爆款", "简约", "高端"]
            if preferences["preferred_styles"]:
                # 将偏好风格放在前面
                preferred = preferences["preferred_styles"][0]
                if preferred in base_styles:
                    base_styles.remove(preferred)
                    base_styles.insert(0, preferred)
            
            for style in base_styles:
                # 构建包含历史偏好的上下文信息
                enhanced_product_info = product_info
                if contextual_suggestions:
                    enhanced_product_info += f"\n\n用户偏好提示: {contextual_suggestions}"
                
                title_result = generate_product_title.invoke({
                    "product_info": enhanced_product_info,
                    "style": style,
                    "target_audience": target_audience
                })
                titles.append({
                    "style": style,
                    "title": title_result
                })
            
            solution["generated_titles"] = titles
            
            # 2. 获取策略建议
            # 从商品信息中提取类型
            product_type = self._extract_product_type(product_info)
            
            # 增强策略输入信息
            enhanced_strategy_input = product_info
            if contextual_suggestions:
                enhanced_strategy_input += f"\n\n用户历史偏好: {contextual_suggestions}"
            if preferences["target_audiences"]:
                enhanced_strategy_input += f"\n\n用户关注的受众群体: {', '.join(preferences['target_audiences'])}"
            
            strategy_result = suggest_strategy.invoke({
                "product_type": product_type,
                "target_audience": target_audience,
                "budget": budget,
                "product_info": enhanced_strategy_input
            })
            
            solution["strategy_suggestion"] = strategy_result
            
            # 3. 评估标题CTR
            # 提取关键词
            import jieba
            keywords = [k for k in jieba.cut(product_info) if len(k) > 1][:5]
            
            ctr_evaluations = []
            for title_info in titles:
                ctr_result = estimate_ctr.invoke({
                    "title": title_info["title"],
                    "keywords": keywords
                })
                
                ctr_evaluations.append({
                    "style": title_info["style"],
                    "title": title_info["title"],
                    "ctr_analysis": ctr_result
                })
            
            solution["ctr_evaluations"] = ctr_evaluations
            
            # 4. 竞品分析（如果提供）
            if competitor_title:
                competitor_analysis = analyze_competitor_title.invoke({
                    "competitor_title": competitor_title,
                    "our_keywords": keywords
                })
                solution["competitor_analysis"] = competitor_analysis
            
            # 5. 推荐最佳标题
            best_title = max(ctr_evaluations, key=lambda x: x["ctr_analysis"]["ctr_score"])
            solution["recommended_title"] = best_title
            
            solution["success"] = True
            
        except Exception as e:
            solution["success"] = False
            solution["error"] = str(e)
        
        return solution
    
    def _extract_product_type(self, product_info: str) -> str:
        """从商品信息中提取商品类型"""
        type_keywords = {
            "服装": ["连衣裙", "衬衫", "T恤", "裤子", "裙子", "外套", "服装"],
            "数码": ["手机", "电脑", "耳机", "平板", "充电器", "数码"],
            "美妆": ["口红", "粉底", "面膜", "护肤", "化妆品", "美妆"],
            "家居": ["床单", "枕头", "台灯", "收纳", "家具", "家居"],
            "食品": ["零食", "茶叶", "咖啡", "糖果", "食品"]
        }
        
        for category, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in product_info:
                    return category
        
        return "服装"  # 默认类型
    
    def extract_user_preferences_from_history(self) -> dict:
        """从对话历史中提取用户偏好"""
        messages = self.memory.chat_memory.messages
        preferences = {
            "preferred_styles": [],
            "target_audiences": [],
            "keywords_liked": [],
            "keywords_disliked": [],
            "price_ranges": [],
            "product_types": []
        }
        
        # 分析历史消息
        for message in messages[-10:]:  # 只分析最近10条消息
            content = str(message.content).lower()
            
            # 提取偏好的风格
            for style in ["爆款", "简约", "高端"]:
                if style in content and ("喜欢" in content or "好" in content or "棒" in content):
                    preferences["preferred_styles"].append(style)
            
            # 提取目标受众
            for audience in ["年轻女性", "中年女性", "年轻男性", "学生"]:
                if audience in content:
                    preferences["target_audiences"].append(audience)
            
            # 提取反馈关键词
            if "不好" in content or "不行" in content or "不喜欢" in content:
                # 提取负面反馈相关的词汇
                words = content.split()
                for i, word in enumerate(words):
                    if word in ["不好", "不行", "不喜欢"] and i > 0:
                        preferences["keywords_disliked"].append(words[i-1])
        
        # 去重和统计频次
        for key in preferences:
            if preferences[key]:
                from collections import Counter
                counter = Counter(preferences[key])
                preferences[key] = [item for item, count in counter.most_common(3)]
        
        return preferences
    
    def get_contextual_suggestions(self, product_info: str, target_audience: str) -> str:
        """基于历史偏好生成上下文建议"""
        preferences = self.extract_user_preferences_from_history()
        
        suggestions = []
        
        # 基于偏好风格建议
        if preferences["preferred_styles"]:
            preferred_style = preferences["preferred_styles"][0]
            suggestions.append(f"根据您之前的偏好，建议使用{preferred_style}风格")
        
        # 基于受众历史建议
        if preferences["target_audiences"] and target_audience in preferences["target_audiences"]:
            suggestions.append(f"您经常关注{target_audience}群体，我会特别注重这个群体的特点")
        
        # 基于负面反馈调整
        if preferences["keywords_disliked"]:
            suggestions.append(f"我会避免使用您不喜欢的词汇：{', '.join(preferences['keywords_disliked'][:2])}")
        
        return "; ".join(suggestions) if suggestions else ""


class MockLLM:
    """模拟LLM类，用于在没有真实LLM服务时提供基础功能"""
    
    def __init__(self):
        self.temperature = 0.7
    
    def bind(self, **kwargs):
        """LangChain期望的bind方法，返回自身以支持链式调用"""
        return self
    
    def invoke(self, prompt: str) -> str:
        """模拟LLM调用"""
        return "这是一个模拟回复，请配置真实的LLM服务以获得更好的体验。"
    
    def __call__(self, prompt: str) -> str:
        return self.invoke(prompt)