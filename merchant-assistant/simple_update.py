# -*- coding: utf-8 -*-
"""
简化的知识库更新脚本
"""

import os
import sys
from config import Config
from knowledge.vector_store import MerchantKnowledgeBase

def main():
    print("商家智能助手 - 知识库更新")
    print("=" * 50)
    
    # 列出知识文档
    knowledge_dir = "knowledge"
    documents = []
    for ext in ["*.md", "*.txt"]:
        import glob
        files = glob.glob(os.path.join(knowledge_dir, ext))
        documents.extend(files)
    
    print(f"发现 {len(documents)} 个知识文档:")
    for i, doc in enumerate(documents, 1):
        file_name = os.path.basename(doc)
        print(f"  {i}. {file_name}")
    
    # 选择embedding类型
    print("\n选择embedding模型:")
    print("1. 模拟模式 (mock) - 快速，用于演示")
    print("2. 中文模型 (sentence_transformers) - 真实效果")
    
    choice = input("请选择 (1-2): ").strip()
    
    if choice == "2":
        embedding_type = "sentence_transformers"
        Config.DEFAULT_EMBEDDING = "sentence_transformers"
        print("选择了真实embedding模型")
    else:
        embedding_type = "mock"
        print("选择了模拟embedding模型")
    
    # 重建知识库
    print("\n正在重建知识库...")
    try:
        kb = MerchantKnowledgeBase(embedding_type=embedding_type)
        kb.build_vector_store(force_rebuild=True)
        
        # 测试搜索
        print("\n测试搜索功能:")
        test_query = "如何优化商品标题"
        results = kb.search(test_query, k=3)
        
        if results:
            print(f"查询 '{test_query}' 找到 {len(results)} 个结果")
            for i, result in enumerate(results):
                source = result["metadata"].get("source", "未知")
                print(f"  {i+1}. 来源: {source}")
        else:
            print("搜索测试失败")
        
        # 统计信息
        stats = kb.get_stats()
        print(f"\n知识库统计:")
        print(f"  源文档数: {stats['source_file_count']}")
        print(f"  向量存储: {'已建立' if stats['vector_store_exists'] else '未建立'}")
        
        print("\n[OK] 知识库更新成功!")
        
    except Exception as e:
        print(f"\n[ERROR] 更新失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()