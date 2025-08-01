# -*- coding: utf-8 -*-
"""
embedding模型管理模块
支持多种embedding模型的统一接口
"""

import os
import sys
from typing import List, Any
import numpy as np

# 添加项目根目录到path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class BaseEmbeddingModel:
    """Embedding模型基类"""
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        raise NotImplementedError
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        raise NotImplementedError


class MockEmbeddingModel(BaseEmbeddingModel):
    """模拟Embedding模型"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        print(f"使用模拟Embedding模型 (维度: {dimension})")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """生成随机向量作为embedding"""
        return np.random.randn(len(texts), self.dimension).astype(np.float32)
    
    def get_dimension(self) -> int:
        return self.dimension


class SentenceTransformersModel(BaseEmbeddingModel):
    """SentenceTransformers模型"""
    
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"正在加载Embedding模型: {self.model_name}")
            
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            
            print(f"✅ Embedding模型加载成功: {self.model_name}")
            print(f"   设备: {self.device}")
            print(f"   维度: {self.get_dimension()}")
            
        except ImportError:
            print("❌ sentence-transformers未安装")
            print("请运行: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"❌ Embedding模型加载失败: {e}")
            raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        if self.model is None:
            raise RuntimeError("模型未加载")
        
        # 批量编码
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        
        return embeddings.astype(np.float32)
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        if self.model is None:
            # 根据常见模型返回预期维度
            dimension_map = {
                "shibing624/text2vec-base-chinese": 768,
                "BAAI/bge-large-zh-v1.5": 1024,
                "BAAI/bge-base-zh-v1.5": 768,
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384
            }
            return dimension_map.get(self.model_name, 768)
        
        return self.model.get_sentence_embedding_dimension()


def create_embedding_model(embedding_type: str = None) -> BaseEmbeddingModel:
    """
    创建embedding模型实例
    
    Args:
        embedding_type: embedding类型
        
    Returns:
        BaseEmbeddingModel实例
    """
    embedding_type = embedding_type or Config.DEFAULT_EMBEDDING
    config = Config.get_embedding_config(embedding_type)
    
    if config["type"] == "mock":
        return MockEmbeddingModel()
    
    elif config["type"] == "sentence_transformers":
        return SentenceTransformersModel(
            model_name=config["model_name"],
            device=config.get("device", "cpu")
        )
    
    else:
        print(f"未知embedding类型: {config['type']}，使用模拟模式")
        return MockEmbeddingModel()


def test_embedding_model():
    """测试embedding模型"""
    print("=" * 50)
    print("测试Embedding模型")
    print("=" * 50)
    
    # 测试文本
    test_texts = [
        "这是一个商品标题生成的测试",
        "电商运营策略优化方案",
        "CTR效果评估与分析"
    ]
    
    # 测试不同配置
    for embedding_type in ["mock", "sentence_transformers"]:
        try:
            print(f"\n测试 {embedding_type} 模型:")
            model = create_embedding_model(embedding_type)
            
            # 编码测试
            embeddings = model.encode(test_texts)
            print(f"   文本数量: {len(test_texts)}")
            print(f"   向量形状: {embeddings.shape}")
            print(f"   向量维度: {model.get_dimension()}")
            print(f"   数据类型: {embeddings.dtype}")
            
            # 计算相似度示例
            if len(embeddings) >= 2:
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                print(f"   相似度示例: {similarity:.4f}")
            
            print(f"   ✅ {embedding_type} 模型测试成功")
            
        except Exception as e:
            print(f"   ❌ {embedding_type} 模型测试失败: {e}")


if __name__ == "__main__":
    test_embedding_model()