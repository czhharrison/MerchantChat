# -*- coding: utf-8 -*-
"""
商家智能助手系统配置文件
生产环境和开发环境的模型服务配置
"""

import os
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    # 基础配置
    PROJECT_NAME = "商家智能助手"
    VERSION = "1.0.0"
    
    # LLM配置
    LLM_CONFIGS = {
        "mock": {
            "type": "mock",
            "description": "模拟LLM，用于演示和测试"
        },
        "ollama_qwen": {
            "type": "ollama",
            "model_name": "qwen2.5:7b",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
            "description": "Ollama本地部署的Qwen2.5模型"
        },
        "ollama_qwen_large": {
            "type": "ollama", 
            "model_name": "qwen2.5:14b",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
            "description": "Ollama本地部署的Qwen2.5大模型"
        }
    }
    
    # Embedding配置
    EMBEDDING_CONFIGS = {
        "mock": {
            "type": "mock",
            "description": "模拟embedding，用于演示"
        },
        "sentence_transformers": {
            "type": "sentence_transformers",
            "model_name": "shibing624/text2vec-base-chinese",
            "device": "cuda",
            "description": "中文文本向量化模型"
        },
        "sentence_transformers_large": {
            "type": "sentence_transformers", 
            "model_name": "BAAI/bge-large-zh-v1.5",
            "device": "cuda",
            "description": "大型中文向量化模型"
        }
    }
    
    # 默认配置
    DEFAULT_LLM = "mock"  # 可选: mock, ollama_qwen, ollama_qwen_large
    DEFAULT_EMBEDDING = "mock"  # 可选: mock, sentence_transformers, sentence_transformers_large
    
    # 知识库配置
    KNOWLEDGE_BASE_CONFIG = {
        "vector_store_path": "knowledge/vector_store",
        "documents_path": "knowledge/documents",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "top_k": 5
    }
    
    # Web界面配置
    STREAMLIT_CONFIG = {
        "page_title": "商家智能助手",
        "page_icon": "🛍️",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    @classmethod
    def get_llm_config(cls, llm_type: str = None) -> Dict[str, Any]:
        """获取LLM配置"""
        llm_type = llm_type or cls.DEFAULT_LLM
        return cls.LLM_CONFIGS.get(llm_type, cls.LLM_CONFIGS["mock"])
    
    @classmethod
    def get_embedding_config(cls, embedding_type: str = None) -> Dict[str, Any]:
        """获取Embedding配置"""
        embedding_type = embedding_type or cls.DEFAULT_EMBEDDING
        return cls.EMBEDDING_CONFIGS.get(embedding_type, cls.EMBEDDING_CONFIGS["mock"])
    
    @classmethod
    def set_production_mode(cls):
        """设置为生产模式"""
        cls.DEFAULT_LLM = "ollama_qwen"
        cls.DEFAULT_EMBEDDING = "sentence_transformers"
    
    @classmethod
    def set_development_mode(cls):
        """设置为开发模式"""
        cls.DEFAULT_LLM = "mock"
        cls.DEFAULT_EMBEDDING = "mock"


# 环境变量配置
def load_env_config():
    """从环境变量加载配置"""
    llm_type = os.getenv("LLM_TYPE", Config.DEFAULT_LLM)
    embedding_type = os.getenv("EMBEDDING_TYPE", Config.DEFAULT_EMBEDDING)
    
    if llm_type in Config.LLM_CONFIGS:
        Config.DEFAULT_LLM = llm_type
    
    if embedding_type in Config.EMBEDDING_CONFIGS:
        Config.DEFAULT_EMBEDDING = embedding_type

# 自动加载环境配置
load_env_config()
