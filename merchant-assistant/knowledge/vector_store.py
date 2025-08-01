# -*- coding: utf-8 -*-
"""
商家知识库向量存储和检索模块
支持文档加载、向量化存储和语义检索
"""

import os
import glob
import sys
from typing import List, Dict, Any, Optional
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# 添加项目根目录到path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from knowledge.embedding_models import create_embedding_model


class MerchantKnowledgeBase:
    """商家知识库类"""
    
    def __init__(self, knowledge_dir: str = None, vector_store_path: str = None, embedding_type: str = None):
        """
        初始化知识库
        
        Args:
            knowledge_dir: 知识文档目录
            vector_store_path: 向量库存储路径
            embedding_type: embedding模型类型
        """
        self.knowledge_dir = knowledge_dir or os.path.join(os.path.dirname(__file__))
        self.vector_store_path = vector_store_path or os.path.join(self.knowledge_dir, "vector_store")
        self.embedding_type = embedding_type or Config.DEFAULT_EMBEDDING
        
        # 初始化文本分割器
        kb_config = Config.KNOWLEDGE_BASE_CONFIG
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=kb_config["chunk_size"],
            chunk_overlap=kb_config["chunk_overlap"],
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
        
        # 初始化嵌入模型
        self.embeddings = self._init_embeddings()
        
        # 向量库
        self.vector_store = None
        
        # 尝试加载已存在的向量库
        self._load_existing_vector_store()
    
    def _init_embeddings(self):
        """初始化嵌入模型"""
        try:
            embedding_model = create_embedding_model(self.embedding_type)
            return LangChainEmbeddingWrapper(embedding_model)
        except Exception as e:
            print(f"Embedding模型初始化失败: {e}")
            print("回退到模拟embedding模型")
            return MockEmbeddings()
    
    def _load_existing_vector_store(self):
        """加载已存在的向量库"""
        if os.path.exists(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"成功加载已存在的向量库: {self.vector_store_path}")
            except Exception as e:
                print(f"Warning: 加载向量库失败: {e}")
    
    def load_documents(self) -> List[Document]:
        """加载知识文档"""
        documents = []
        
        # 支持的文件类型
        file_patterns = ["*.md", "*.txt"]
        
        for pattern in file_patterns:
            file_path = os.path.join(self.knowledge_dir, pattern)
            files = glob.glob(file_path)
            
            for file in files:
                try:
                    loader = TextLoader(file, encoding='utf-8')
                    docs = loader.load()
                    
                    # 添加文件来源信息
                    for doc in docs:
                        doc.metadata['source'] = os.path.basename(file)
                        doc.metadata['file_type'] = os.path.splitext(file)[1]
                    
                    documents.extend(docs)
                    print(f"加载文档: {os.path.basename(file)}")
                    
                except Exception as e:
                    print(f"Warning: 加载文档失败 {file}: {e}")
        
        if not documents:
            # 如果没有找到文档，创建一些基础文档
            documents = self._create_default_documents()
        
        return documents
    
    def _create_default_documents(self) -> List[Document]:
        """创建默认知识文档"""
        default_docs = [
            Document(
                page_content="""
                商品标题优化原则：
                1. 关键词前置：将核心关键词放在标题前部
                2. 长度适中：建议20-30字符之间
                3. 突出卖点：强调独特优势和价值点
                4. 营造紧急感：使用"限时"、"抢购"等词汇
                5. 符合规范：避免极限词和违禁词汇
                """,
                metadata={"source": "default", "category": "标题优化"}
            ),
            Document(
                page_content="""
                不同受众营销策略：
                年轻女性：追求时尚个性，偏好小红书抖音，适合KOL种草营销
                中年女性：注重品质实用，偏好淘宝京东，适合品质保证宣传
                年轻男性：关注科技效率，偏好京东B站，适合技术参数对比
                学生群体：价格敏感，偏好拼多多，适合性价比突出营销
                """,
                metadata={"source": "default", "category": "营销策略"}
            ),
            Document(
                page_content="""
                电商平台活动节点：
                双11（11月11日）：全年最大促销节点，需提前2个月备货
                618（6月18日）：年中大促，数码电器类重点节点
                双12（12月12日）：中小商家主场，个性化商品推广
                38女王节（3月8日）：女性商品专场，美妆服饰重点
                99划算节（9月9日）：性价比商品推广，9.9包邮
                """,
                metadata={"source": "default", "category": "平台活动"}
            )
        ]
        
        print("创建默认知识文档")
        return default_docs
    
    def build_vector_store(self, force_rebuild: bool = False):
        """构建向量库"""
        
        # 如果已存在向量库且不强制重建，则跳过
        if self.vector_store and not force_rebuild:
            print("向量库已存在，如需重建请设置 force_rebuild=True")
            return
        
        print("开始构建向量库...")
        
        # 加载文档
        documents = self.load_documents()
        
        if not documents:
            print("❌ 没有找到可加载的文档")
            return
        
        # 分割文档
        print(f"正在分割 {len(documents)} 个文档...")
        texts = self.text_splitter.split_documents(documents)
        print(f"文档分割完成，共 {len(texts)} 个文本块")
        
        # 构建向量库
        print("正在构建向量库...")
        try:
            self.vector_store = FAISS.from_documents(texts, self.embeddings)
            
            # 保存向量库
            os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
            self.vector_store.save_local(self.vector_store_path)
            
            print(f"向量库构建成功，保存至: {self.vector_store_path}")
            
        except Exception as e:
            print(f"向量库构建失败: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询问题
            k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        if not self.vector_store:
            return []
        
        try:
            # 执行相似度搜索
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_relevant_context(self, query: str, max_length: int = 1000) -> str:
        """
        获取相关上下文信息
        
        Args:
            query: 查询问题
            max_length: 最大返回长度
            
        Returns:
            相关上下文字符串
        """
        results = self.search(query, k=3)
        
        if not results:
            return "未找到相关信息。"
        
        context_parts = []
        current_length = 0
        
        for result in results:
            content = result["content"].strip()
            source = result["metadata"].get("source", "未知来源")
            
            part = f"[来源: {source}]\n{content}\n"
            
            if current_length + len(part) <= max_length:
                context_parts.append(part)
                current_length += len(part)
            else:
                break
        
        return "\n".join(context_parts)
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None):
        """
        添加新文档到向量库
        
        Args:
            content: 文档内容
            metadata: 文档元数据
        """
        if not self.vector_store:
            print("向量库未初始化，请先构建向量库")
            return
        
        # 创建文档
        doc = Document(
            page_content=content,
            metadata=metadata or {}
        )
        
        # 分割文档
        texts = self.text_splitter.split_documents([doc])
        
        # 添加到向量库
        try:
            self.vector_store.add_documents(texts)
            # 保存更新后的向量库
            self.vector_store.save_local(self.vector_store_path)
            print("文档添加成功")
            
        except Exception as e:
            print(f"文档添加失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = {
            "vector_store_exists": self.vector_store is not None,
            "vector_store_path": self.vector_store_path,
            "knowledge_dir": self.knowledge_dir
        }
        
        if self.vector_store:
            try:
                # 获取向量库中的文档数量
                stats["document_count"] = self.vector_store.index.ntotal
            except:
                stats["document_count"] = "未知"
        else:
            stats["document_count"] = 0
        
        # 统计知识文档文件
        file_count = 0
        for pattern in ["*.md", "*.txt"]:
            file_path = os.path.join(self.knowledge_dir, pattern)
            file_count += len(glob.glob(file_path))
        
        stats["source_file_count"] = file_count
        
        return stats


class LangChainEmbeddingWrapper:
    """将我们的embedding模型包装为LangChain兼容接口"""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档列表"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        embedding = self.embedding_model.encode([text])
        return embedding[0].tolist()


class MockEmbeddings:
    """模拟嵌入模型，用于测试"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档列表"""
        import hashlib
        import json
        
        embeddings = []
        for text in texts:
            # 使用文本hash生成伪随机向量
            hash_obj = hashlib.md5(text.encode())
            hash_int = int(hash_obj.hexdigest(), 16)
            
            # 生成384维向量（模拟sentence-transformers输出）
            vector = []
            for i in range(384):
                vector.append((hash_int % 1000 + i) / 1000.0 - 0.5)
                hash_int = hash_int // 1000 + i
            
            embeddings.append(vector)
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self.embed_documents([text])[0]