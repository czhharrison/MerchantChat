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
    analyze_competitor_title
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
        
        # 初始化工具
        self.tools = self._init_tools()
        
        # 初始化记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
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
            max_iterations=5,
            early_stopping_method="generate"
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
        处理用户请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果字典
        """
        try:
            # 执行Agent
            result = self.agent_executor.invoke({"input": user_input})
            
            return {
                "success": True,
                "response": result["output"],
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"抱歉，处理您的请求时出现了错误：{str(e)}"
            }
    
    def generate_complete_solution(self, product_info: str, 
                                 competitor_title: str = None,
                                 target_audience: str = "通用",
                                 budget: str = "中等") -> Dict[str, Any]:
        """
        生成完整的商品优化解决方案
        
        Args:
            product_info: 商品信息
            competitor_title: 竞品标题（可选）
            target_audience: 目标受众
            budget: 预算水平
            
        Returns:
            完整解决方案
        """
        
        solution = {
            "product_info": product_info,
            "target_audience": target_audience,
            "budget": budget
        }
        
        try:
            # 1. 生成商品标题（多个版本）
            titles = []
            styles = ["爆款", "简约", "高端"]
            
            for style in styles:
                title_result = generate_product_title.invoke({
                    "product_info": product_info,
                    "style": style
                })
                titles.append({
                    "style": style,
                    "title": title_result
                })
            
            solution["generated_titles"] = titles
            
            # 2. 获取策略建议
            # 从商品信息中提取类型
            product_type = self._extract_product_type(product_info)
            
            strategy_result = suggest_strategy.invoke({
                "product_type": product_type,
                "target_audience": target_audience,
                "budget": budget
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


class MockLLM:
    """模拟LLM类，用于在没有真实LLM服务时提供基础功能"""
    
    def __init__(self):
        self.temperature = 0.7
    
    def bind(self, **kwargs):
        """LangChain期望的bind方法，返回自身以支持链式调用"""
        return self
    
    def invoke(self, prompt: str) -> str:
        """模拟LLM调用"""
        # 简化的Agent响应逻辑
        if "Question:" in prompt or "用户输入：" in prompt:
            # 提取用户输入
            lines = prompt.split('\n')
            user_input = ""
            for line in lines:
                if "用户输入：" in line:
                    user_input = line.split("用户输入：")[-1].strip()
                    break
            
            # 基于关键词生成响应
            if "标题" in user_input:
                return """Thought: 用户需要生成商品标题，我应该使用generate_product_title工具
Action: generate_product_title
Action Input: {"product_info": "商品信息", "style": "爆款"}
Observation: 【热销爆款】商品名称，品质保证
Thought: 现在我知道最终答案了
Final Answer: 我为您生成了一个爆款风格的商品标题：【热销爆款】商品名称，品质保证。这个标题突出了商品的热销特点和品质保证，能够吸引用户点击。"""
                
            elif "策略" in user_input:
                return """Thought: 用户需要营销策略建议，我应该使用suggest_strategy工具
Action: suggest_strategy  
Action Input: {"product_type": "服装", "target_audience": "年轻女性", "budget": "中等"}
Observation: 建议采用抖音话题挑战营销，配合KOL合作推广
Thought: 现在我知道最终答案了
Final Answer: 根据您的需求，我建议采用以下营销策略：参与抖音话题挑战，使用时尚穿搭等标签，配合KOL合作进行推广。这种策略适合年轻女性群体，能够有效提升品牌知名度和转化率。"""
                
            elif "CTR" in user_input or "评估" in user_input:
                return """Thought: 用户需要CTR评估，我应该使用estimate_ctr工具
Action: estimate_ctr
Action Input: {"title": "商品标题", "keywords": ["关键词1", "关键词2"]}
Observation: {"ctr_score": 0.85, "ctr_percentage": "85%", "recommendations": ["优化建议"]}
Thought: 现在我知道最终答案了
Final Answer: 经过分析，该标题的CTR评分为85%，整体质量较好。建议可以进一步优化关键词覆盖率和标题长度以获得更好的效果。"""
                
            else:
                return f"""Thought: 用户的问题是关于商家运营的，我需要提供专业建议
Thought: 现在我知道最终答案了
Final Answer: 感谢您的咨询！作为电商运营顾问助手，我可以帮您解决商品标题优化、营销策略制定、CTR效果评估等问题。请告诉我您的具体需求，我会为您提供专业的建议。"""
        
        return "这是一个模拟回复，请配置真实的LLM服务以获得更好的体验。"
    
    def __call__(self, prompt: str) -> str:
        return self.invoke(prompt)