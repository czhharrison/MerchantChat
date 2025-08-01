# -*- coding: utf-8 -*-
"""
构建商家知识库脚本
加载文档并构建向量存储
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge.vector_store import MerchantKnowledgeBase


def main():
    """主函数"""
    print("开始构建商家智能助手知识库")
    print("=" * 50)
    
    # 初始化知识库
    kb = MerchantKnowledgeBase()
    
    # 显示当前状态
    stats = kb.get_stats()
    print(f"\n知识库状态:")
    print(f"  知识文档目录: {stats['knowledge_dir']}")
    print(f"  向量库路径: {stats['vector_store_path']}")
    print(f"  源文件数量: {stats['source_file_count']}")
    print(f"  向量库存在: {stats['vector_store_exists']}")
    
    # 构建向量库
    print(f"\n开始构建向量库...")
    kb.build_vector_store(force_rebuild=True)
    
    # 测试搜索功能
    print(f"\n测试搜索功能:")
    test_queries = [
        "如何优化商品标题",
        "年轻女性营销策略",
        "电商平台活动时间",
        "CTR评估方法"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = kb.search(query, k=2)
        
        if results:
            for i, result in enumerate(results, 1):
                source = result['metadata'].get('source', '未知')
                score = result['similarity_score']
                content = result['content'][:100] + "..."
                print(f"  结果{i} (来源:{source}, 相似度:{score:.3f}): {content}")
        else:
            print("  未找到相关结果")
    
    # 测试上下文获取
    print(f"\n测试上下文获取:")
    context = kb.get_relevant_context("如何为连衣裙写标题", max_length=500)
    print(f"相关上下文:\n{context}")
    
    # 最终统计
    final_stats = kb.get_stats()
    print(f"\n" + "=" * 50)
    print("知识库构建完成!")
    print(f"向量库文档数量: {final_stats['document_count']}")
    print("=" * 50)


if __name__ == "__main__":
    main()