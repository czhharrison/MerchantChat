# -*- coding: utf-8 -*-
"""
更新知识库脚本
支持使用真实embedding模型重建向量存储
"""

import os
import sys
import shutil
from config import Config
from knowledge.vector_store import MerchantKnowledgeBase

def print_separator(title=""):
    """打印分隔线"""
    print("=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def backup_existing_knowledge_base():
    """备份现有知识库"""
    knowledge_dir = "knowledge"
    vector_store_path = os.path.join(knowledge_dir, "vector_store")
    backup_path = os.path.join(knowledge_dir, "vector_store_backup")
    
    if os.path.exists(vector_store_path):
        try:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(vector_store_path, backup_path)
            print(f"[OK] 已备份现有知识库到: {backup_path}")
            return True
        except Exception as e:
            print(f"[ERROR] 备份失败: {e}")
            return False
    else:
        print("[INFO] 未发现现有知识库，跳过备份")
        return True

def list_knowledge_documents():
    """列出知识库文档"""
    print_separator("知识库文档清单")
    
    knowledge_dir = "knowledge"
    documents = []
    
    for ext in ["*.md", "*.txt"]:
        import glob
        files = glob.glob(os.path.join(knowledge_dir, ext))
        documents.extend(files)
    
    if documents:
        print(f"发现 {len(documents)} 个知识文档:")
        for i, doc in enumerate(documents, 1):
            file_name = os.path.basename(doc)
            file_size = os.path.getsize(doc)
            print(f"  {i}. {file_name} ({file_size} bytes)")
    else:
        print("[ERROR] 未发现知识文档")
        return False
    
    return True

def test_embedding_model(embedding_type):
    """测试embedding模型"""
    print_separator(f"测试 {embedding_type} Embedding模型")
    
    try:
        from knowledge.embedding_models import create_embedding_model
        
        model = create_embedding_model(embedding_type)
        
        # 测试编码
        test_texts = [
            "商品标题优化策略",
            "电商营销推广方案", 
            "用户转化率分析"
        ]
        
        print("正在测试embedding模型...")
        embeddings = model.encode(test_texts)
        
        print(f"[OK] 模型测试成功:")
        print(f"   模型类型: {embedding_type}")
        print(f"   向量维度: {model.get_dimension()}")
        print(f"   测试文本数: {len(test_texts)}")
        print(f"   输出向量形状: {embeddings.shape}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 模型测试失败: {e}")
        return False

def rebuild_vector_store(embedding_type="sentence_transformers", force=True):
    """重建向量存储"""
    print_separator(f"使用 {embedding_type} 模型重建向量库")
    
    try:
        # 初始化知识库
        kb = MerchantKnowledgeBase(embedding_type=embedding_type)
        
        # 重建向量库
        kb.build_vector_store(force_rebuild=force)
        
        # 测试搜索功能
        print("\n测试搜索功能...")
        test_queries = [
            "如何优化商品标题",
            "营销策略推荐",
            "消费者心理分析"
        ]
        
        for query in test_queries:
            results = kb.search(query, k=2)
            if results:
                print(f"[OK] 查询 '{query}' - 找到 {len(results)} 个相关结果")
                for i, result in enumerate(results):
                    source = result["metadata"].get("source", "未知")
                    score = result["similarity_score"]
                    print(f"   {i+1}. 来源: {source}, 相似度: {score:.4f}")
            else:
                print(f"[ERROR] 查询 '{query}' - 未找到结果")
        
        # 显示统计信息
        stats = kb.get_stats()
        print(f"\n[INFO] 知识库统计:")
        print(f"   源文档数: {stats['source_file_count']}")
        print(f"   向量存储: {'[OK] 已建立' if stats['vector_store_exists'] else '[ERROR] 未建立'}")
        print(f"   存储路径: {stats['vector_store_path']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 向量库重建失败: {e}")
        return False

def update_configuration():
    """更新配置为生产模式"""
    print_separator("更新系统配置")
    
    # 检查当前配置
    print(f"当前LLM配置: {Config.DEFAULT_LLM}")
    print(f"当前Embedding配置: {Config.DEFAULT_EMBEDDING}")
    
    # 提示用户选择
    print("\n配置选项:")
    print("1. 设置为生产模式 (ollama_qwen + sentence_transformers)")
    print("2. 设置为开发模式 (mock + mock)")
    print("3. 保持当前配置")
    
    choice = input("请选择配置模式 (1-3): ").strip()
    
    if choice == "1":
        Config.set_production_mode()
        print("[OK] 已设置为生产模式")
    elif choice == "2":
        Config.set_development_mode()
        print("[OK] 已设置为开发模式")
    else:
        print("[INFO] 保持当前配置")
    
    print(f"最终LLM配置: {Config.DEFAULT_LLM}")
    print(f"最终Embedding配置: {Config.DEFAULT_EMBEDDING}")

def install_dependencies():
    """安装必要依赖"""
    print_separator("检查和安装依赖")
    
    required_packages = [
        "sentence-transformers",
        "torch",
        "transformers"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"[ERROR] {package} 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        install = input("是否自动安装? (y/N): ").lower().strip()
        
        if install == 'y':
            import subprocess
            for package in missing_packages:
                try:
                    print(f"正在安装 {package}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"[OK] {package} 安装成功")
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR] {package} 安装失败: {e}")
                    return False
            return True
        else:
            print("请手动安装依赖包:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    else:
        print("[OK] 所有依赖都已安装")
        return True

def main():
    """主函数"""
    print_separator("商家智能助手 - 知识库更新工具")
    
    print("此工具将帮助您:")
    print("1. 检查和安装必要依赖")
    print("2. 配置真实的embedding模型")
    print("3. 扩展知识库内容") 
    print("4. 重建向量存储")
    print("5. 测试系统功能")
    
    # 步骤1: 依赖检查
    if not install_dependencies():
        print("\n❌ 依赖安装失败，请手动安装后重试")
        return
    
    # 步骤2: 文档清单
    if not list_knowledge_documents():
        print("\n❌ 未发现知识文档，无法继续")
        return
    
    # 步骤3: 配置更新
    update_configuration()
    embedding_type = Config.DEFAULT_EMBEDDING
    
    # 步骤4: 测试embedding模型
    if embedding_type != "mock":
        if not test_embedding_model(embedding_type):
            print(f"\n❌ {embedding_type} 模型测试失败")
            fallback = input("是否使用mock模式继续? (y/N): ").lower().strip()
            if fallback == 'y':
                embedding_type = "mock"
            else:
                return
    
    # 步骤5: 备份现有知识库
    if not backup_existing_knowledge_base():
        proceed = input("备份失败，是否继续? (y/N): ").lower().strip()
        if proceed != 'y':
            return
    
    # 步骤6: 重建向量库
    if not rebuild_vector_store(embedding_type):
        print("\n❌ 向量库重建失败")
        return
    
    # 完成
    print_separator("更新完成")
    print("✅ 知识库更新成功!")
    print("\n接下来可以:")
    print("1. 运行 python test_fixed.py 测试系统")
    print("2. 启动 Web 界面: cd ui && streamlit run streamlit_app.py")
    print("3. 配置 Ollama 服务以使用真实LLM")
    
    print(f"\n📋 当前配置:")
    print(f"   LLM: {Config.DEFAULT_LLM}")
    print(f"   Embedding: {Config.DEFAULT_EMBEDDING}")
    print(f"   知识库: {len(os.listdir('knowledge'))} 个文件")

if __name__ == "__main__":
    main()