# 商家智能助手系统 - 项目运行指南

## 📋 目录
- [项目概述](#项目概述)
- [环境准备](#环境准备)
- [安装依赖](#安装依赖)
- [系统组件介绍](#系统组件介绍)
- [运行步骤](#运行步骤)
- [功能使用说明](#功能使用说明)
- [命令详解](#命令详解)
- [错误排查](#错误排查)
- [知识库扩展](#知识库扩展)

## 项目概述

商家智能助手系统是一个基于RAG架构和LLM Agent的智能运营平台，为电商商家提供：
- 智能标题生成
- 营销策略推荐  
- CTR效果评估
- 竞品分析
- 知识库问答

### 核心技术栈
- **LangChain**: 开源AI应用框架，用于构建Agent和工具链
- **Streamlit**: 开源Python Web应用框架，用于快速构建数据应用界面
- **FAISS**: Facebook开源的向量相似度搜索库
- **jieba**: 开源中文分词库
- **sentence-transformers**: 开源文本嵌入模型库

## 环境准备

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.14+, Linux
- **Python版本**: 3.8 - 3.11 (推荐3.10)
- **内存**: 最少4GB，推荐8GB以上
- **存储空间**: 2GB可用空间

### Python环境检查
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version
```

## 安装依赖

### 方式一：一键安装（推荐）
```bash
# 进入项目目录
cd D:\project\MerchantChat

# 安装所有依赖
pip install langchain langchain-community faiss-cpu streamlit jieba sentence-transformers
```

### 方式二：分步安装
```bash
# 核心框架
pip install langchain langchain-community

# 向量数据库
pip install faiss-cpu

# Web界面框架
pip install streamlit

# 中文处理
pip install jieba

# 文本嵌入（可选，用于真实embedding）
pip install sentence-transformers
```

### 依赖说明
| 库名 | 版本要求 | 作用 | 来源 |
|------|----------|------|------|
| langchain | >=0.3.0 | Agent框架和工具管理 | 开源框架 |
| langchain-community | >=0.3.0 | LangChain社区组件 | 官方扩展 |
| faiss-cpu | >=1.7.4 | 向量相似度搜索 | Facebook开源 |
| streamlit | >=1.32.0 | Web应用界面 | 开源Web框架 |
| jieba | >=0.42.1 | 中文分词 | 开源中文NLP |
| sentence-transformers | >=3.0.0 | 文本向量化 | HuggingFace开源 |

## 系统组件介绍

### 1. Streamlit是什么？
**Streamlit**是一个开源Python库，专门用于快速构建数据科学和机器学习的Web应用。

**特点**：
- 纯Python编写，无需前端开发经验
- 快速原型开发，几分钟即可创建应用
- 自动重载，修改代码后自动刷新
- 丰富的组件：图表、表格、侧边栏、多页面等
- 广泛应用于数据可视化、AI应用演示

**官方网站**: https://streamlit.io/
**开源地址**: https://github.com/streamlit/streamlit

### 2. 项目结构详解
```
MerchantChat/
├── langchain-chatchat/          # 参考框架（已下载）
├── merchant-assistant/          # 主项目目录
│   ├── agent/                   # Agent核心模块
│   │   ├── tools/               # 工具集合
│   │   │   └── merchant_tools.py    # 商家专用工具实现
│   │   ├── templates/           # Prompt模板目录
│   │   └── agent_executor.py    # Agent执行器和控制逻辑
│   ├── knowledge/               # 知识库目录
│   │   ├── merchant_operation_guide.md  # 商家运营指南
│   │   ├── title_templates.md          # 标题模板库
│   │   ├── platform_rules.md           # 平台规则文档
│   │   ├── vector_store.py             # 向量存储管理器
│   │   └── vector_store/               # 向量数据库文件
│   ├── ui/                      # 用户界面
│   │   └── streamlit_app.py     # Streamlit Web应用
│   ├── build_knowledge_base.py  # 知识库构建脚本
│   ├── test_system.py          # 系统测试脚本
│   └── README.md               # 项目说明文档
├── 项目运行指南.md              # 本文档
└── README.md                   # 总体项目说明
```

## 运行步骤

### 第一步：构建知识库
```bash
# 进入项目目录
cd D:\project\MerchantChat\merchant-assistant

# 运行知识库构建脚本
python build_knowledge_base.py
```

**命令作用**：
- 加载knowledge目录下的所有.md和.txt文件
- 使用文本分割器将文档切分为小块
- 将文本块转换为向量表示
- 构建FAISS向量索引用于语义搜索
- 保存向量库到vector_store目录

**预期输出**：
```
开始构建商家智能助手知识库
==================================================
使用模拟embedding模型（用于演示）

知识库状态:
  知识文档目录: D:\project\MerchantChat\merchant-assistant\knowledge
  向量库路径: D:\project\MerchantChat\merchant-assistant\knowledge\vector_store
  源文件数量: 3
  向量库存在: False

开始构建向量库...
加载文档: merchant_operation_guide.md
加载文档: platform_rules.md  
加载文档: title_templates.md
正在分割 3 个文档...
文档分割完成，共 19 个文本块
正在构建向量库...
向量库构建成功，保存至: D:\project\MerchantChat\merchant-assistant\knowledge\vector_store

知识库构建完成!
向量库文档数量: 19
==================================================
```

### 第二步：系统功能测试
```bash
# 在merchant-assistant目录下
python test_system.py
```

**命令作用**：
- 测试所有工具函数（标题生成、策略推荐、CTR评估、竞品分析）
- 验证Agent系统集成
- 检查依赖库导入情况
- 验证系统完整性

**预期输出示例**：
```
商家智能助手系统测试
==================================================
测试工具模块
==================================================

1. 测试标题生成
   爆款风格: 【热销爆款】连衣裙，价格特惠
   简约风格: 连衣裙 | 价格
   高端风格: 精选连衣裙，价格

2. 测试策略推荐
   策略建议: 建议参与抖音话题挑战，使用时尚穿搭、OOTD等标签...

3. 测试CTR评估  
   标题: 【热销爆款】粉色连衣裙，夏季新款特惠
   CTR评分: 92.5%
   关键词覆盖率: 100.00%
   优化建议: ['标题质量良好，可考虑A/B测试不同版本']

测试完成！
启动Web界面命令:
   cd merchant-assistant/ui
   streamlit run streamlit_app.py
```

### 第三步：启动Web界面
```bash
# 进入UI目录
cd D:\project\MerchantChat\merchant-assistant\ui

# 启动Streamlit应用
streamlit run streamlit_app.py
```

**命令作用**：
- 启动Streamlit Web服务器
- 加载商家智能助手Web界面
- 在浏览器中打开应用（通常是http://localhost:8501）

**正常启动输出**：
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

浏览器会自动打开，或手动访问 http://localhost:8501

## 功能使用说明

### Web界面功能说明

#### 1. 一站式解决方案页面
**功能**：输入商品信息，一键生成完整的营销解决方案

**使用步骤**：
1. 在"商品信息"文本框输入：`连衣裙，粉色，夏季新款，价格129元，适合年轻女性`
2. （可选）输入竞品标题：`【夏日清凉】粉色连衣裙女夏季新款显瘦气质裙子`
3. 选择目标受众：年轻女性、中年女性、年轻男性等  
4. 选择预算水平：低、中等、高
5. 点击"🚀 生成完整解决方案"

**输出内容**：
- **推荐标题**：CTR最高的标题及其评分
- **标题候选方案**：3种风格的标题对比
- **营销策略建议**：针对目标受众的具体策略
- **竞品分析**：与竞品的对比和差异化建议

#### 2. 单项工具测试页面
**功能**：独立测试各个功能模块

**标题生成工具**：
- 输入：商品信息
- 选择：标题风格（爆款/简约/高端）
- 输出：生成的标题

**策略推荐工具**：
- 输入：商品类型、目标受众、预算水平
- 输出：营销策略建议

**CTR评估工具**：
- 输入：商品标题、关键词列表
- 输出：CTR评分、覆盖率、优化建议

**竞品分析工具**：
- 输入：竞品标题、我们的关键词
- 输出：对比分析和差异化建议

#### 3. 智能对话页面
**功能**：通过自然语言与AI助手交互

**使用示例**：
- 用户：`帮我为粉色连衣裙生成一个爆款风格的标题`
- 助手：`【热销爆款】粉色连衣裙，夏季新款特惠`

- 用户：`这个标题的CTR大概是多少`
- 助手：`根据评估，该标题的CTR约为92.5%，关键词覆盖率100%...`

#### 4. 分析报告页面
**功能**：查看系统状态和运行演示

**系统状态显示**：
- 可用工具数量
- 对话轮次
- 系统运行状态

## 命令详解

### 1. build_knowledge_base.py详解

**完整命令**：
```bash
cd D:\project\MerchantChat\merchant-assistant
python build_knowledge_base.py
```

**内部执行流程**：
1. **初始化知识库对象**
   ```python
   kb = MerchantKnowledgeBase()
   ```

2. **加载文档**
   - 扫描knowledge目录下的.md/.txt文件
   - 使用TextLoader加载文档内容
   - 添加文档元数据（来源、类型等）

3. **文档分割**
   ```python
   text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=500,      # 每块500字符
       chunk_overlap=50,    # 块间重叠50字符
       separators=["\n\n", "\n", "。", "！", "？"]  # 中文分隔符
   )
   ```

4. **向量化存储**
   - 将文本块转换为向量表示
   - 使用FAISS构建向量索引
   - 保存到vector_store目录

**输出文件**：
- `knowledge/vector_store/index.faiss` - FAISS索引文件
- `knowledge/vector_store/index.pkl` - 索引元数据

### 2. streamlit run详解

**完整命令**：
```bash
cd D:\project\MerchantChat\merchant-assistant\ui
streamlit run streamlit_app.py
```

**Streamlit启动参数（可选）**：
```bash
# 指定端口
streamlit run streamlit_app.py --server.port 8502

# 指定主机
streamlit run streamlit_app.py --server.address 0.0.0.0

# 调试模式
streamlit run streamlit_app.py --logger.level debug
```

**内部执行流程**：
1. **加载应用配置**
2. **初始化session state**
3. **创建Agent实例**
4. **渲染Web界面**
5. **启动Web服务器**

### 3. test_system.py详解

**完整命令**：
```bash
cd D:\project\MerchantChat\merchant-assistant  
python test_system.py
```

**测试项目**：
1. **工具模块测试**
   - generate_product_title.invoke()
   - suggest_strategy.invoke()
   - estimate_ctr.invoke()
   - analyze_competitor_title.invoke()

2. **Agent系统测试**
   - MerchantAssistantAgent初始化
   - generate_complete_solution()
   - process_request()

3. **系统集成测试**
   - 依赖库导入检查
   - 文件存在性验证
   - 功能完整性确认

## 错误排查

### 常见错误1：ValueError: Prompt missing required variables: {'tool_names'}

**错误原因**：LangChain版本更新导致Prompt模板格式变化

**解决方案**：修复Agent执行器中的Prompt模板

**解决步骤**：
已自动修复，重新启动即可。错误原因是Prompt模板缺少`tool_names`变量。

### 常见错误2：知识库文档数量过少

**现象**：运行`python build_knowledge_base.py`后显示"源文件数量: 3"

**说明**：
当前知识库包含3个基础文档：
- `merchant_operation_guide.md` - 商家运营指南（约5000字）
- `title_templates.md` - 标题模板库（约3000字）
- `platform_rules.md` - 平台规则文档（约4000字）

**扩展方法**：
您可以在`knowledge/`目录下添加更多`.md`或`.txt`文件：

1. **添加新文档**：
```bash
# 示例：添加新的营销策略文档
# 在knowledge目录创建new_strategy.md
```

2. **重新构建知识库**：
```bash
cd merchant-assistant
python build_knowledge_base.py
```

3. **推荐扩展内容**：
- 各平台详细规则文档
- 更多行业类目的标题模板
- 成功案例分析
- 数据分析方法
- 客服话术模板

### 常见错误3：模块导入失败

**错误信息**：`ModuleNotFoundError: No module named 'xxx'`

**解决方法**：
```bash
# 重新安装缺失的模块
pip install 模块名

# 或重新安装所有依赖
pip install -r requirements.txt  # 如果有requirements.txt
```

### 常见错误4：端口占用

**错误信息**：`OSError: [Errno 48] Address already in use`

**解决方法**：
```bash
# 指定不同端口启动
streamlit run streamlit_app.py --server.port 8502

# 或杀死占用进程
# Windows:
netstat -ano | findstr 8501
taskkill /PID <进程ID> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill
```

### 常见错误5：编码问题

**错误信息**：`UnicodeEncodeError: 'gbk' codec can't encode character`

**解决方法**：
设置环境变量：
```bash
# Windows CMD
set PYTHONIOENCODING=utf-8

# Windows PowerShell  
$env:PYTHONIOENCODING="utf-8"

# Linux/Mac
export PYTHONIOENCODING=utf-8
```

## 知识库扩展

### 当前知识库结构
```
knowledge/
├── merchant_operation_guide.md    # 商家运营指南
│   ├── 商品标题优化策略
│   ├── 营销策略指南  
│   ├── 平台特色营销
│   ├── 商品定价策略
│   ├── 客户服务优化
│   └── 数据分析与优化
├── title_templates.md             # 标题模板库
│   ├── 服装类标题模板
│   ├── 数码电子类模板
│   ├── 美妆护肤类模板
│   ├── 家居生活类模板
│   ├── 食品饮料类模板
│   ├── 母婴用品类模板
│   ├── 运动户外类模板
│   └── 汽车用品类模板
└── platform_rules.md             # 平台规则文档
    ├── 淘宝天猫平台规则
    ├── 京东平台规则
    ├── 拼多多平台规则
    ├── 抖音电商规则
    ├── 小红书平台规则
    └── 主要电商节点活动
```

### 扩展建议

#### 1. 行业深度文档
```
knowledge/
├── industry_deep/
│   ├── fashion_deep.md           # 服装行业深度分析
│   ├── digital_deep.md           # 数码行业分析
│   ├── beauty_deep.md            # 美妆行业分析
│   └── home_deep.md              # 家居行业分析
```

#### 2. 数据分析文档
```
knowledge/
├── data_analysis/
│   ├── metrics_guide.md          # 关键指标解读
│   ├── ab_testing.md             # A/B测试方法
│   ├── conversion_optimization.md # 转化率优化
│   └── competitor_analysis.md     # 竞品分析方法
```

#### 3. 案例库
```
knowledge/
├── case_studies/
│   ├── success_cases.md          # 成功案例分析
│   ├── failure_lessons.md        # 失败教训总结
│   └── seasonal_campaigns.md     # 季节性营销案例
```

#### 4. 工具指南
```
knowledge/
├── tools_guide/
│   ├── analytics_tools.md        # 分析工具使用
│   ├── design_tools.md           # 设计工具推荐
│   └── automation_tools.md       # 自动化工具
```

### 添加新文档的步骤

1. **创建文档**：
```bash
# 在knowledge目录下创建新文档
cd D:\project\MerchantChat\merchant-assistant\knowledge
# 创建新的.md文件，按照现有文档格式编写内容
```

2. **重新构建向量库**：
```bash
cd D:\project\MerchantChat\merchant-assistant
python build_knowledge_base.py
```

3. **验证加载**：
检查输出中的"源文件数量"是否增加

4. **测试检索**：
在Web界面的智能对话中测试新知识是否可以被检索到

### 文档编写规范

#### 格式要求
- 使用Markdown格式
- 文件编码：UTF-8
- 合理使用标题层级（# ## ### ####）
- 重要信息使用**粗体**标注

#### 内容要求
- 信息准确可靠
- 逻辑结构清晰
- 实用性强，可操作
- 包含具体示例

#### 示例文档结构
```markdown
# 文档标题

## 概述
简要介绍文档内容和适用场景

## 详细内容
### 子章节1
具体内容...

### 子章节2  
具体内容...

## 实践建议
具体可操作的建议

## 相关工具
推荐的工具和资源

## 注意事项
重要提醒和限制条件
```

## 高级使用技巧

### 1. 自定义配置
在Web界面侧边栏可以调整：
- 目标受众设置
- 预算水平设置
- 模型配置（如果需要真实LLM）

### 2. 批量处理
对于大量商品，可以：
- 修改`test_system.py`脚本批量调用工具
- 导出结果到CSV文件
- 使用Python脚本自动化处理

### 3. 集成其他工具
系统支持扩展：
- 添加新的工具函数到`merchant_tools.py`
- 在Agent中注册新工具
- 在Web界面添加新的功能页面

### 4. 数据导出
可以添加数据导出功能：
- 导出标题方案到Excel
- 保存分析报告为PDF
- 批量导出策略建议

## 开发扩展指南

### 添加新工具

1. **在merchant_tools.py中添加新函数**：
```python
@tool
def new_tool_function(param1: str, param2: str) -> str:
    """新工具功能描述"""
    # 工具逻辑实现
    return result
```

2. **在agent_executor.py中注册**：
```python
from .tools.merchant_tools import new_tool_function

def _init_tools(self) -> List[BaseTool]:
    return [
        # 现有工具...
        new_tool_function,  # 添加新工具
    ]
```

3. **在Web界面添加测试**：
在`streamlit_app.py`的单项工具测试中添加新工具的测试界面。

### 扩展知识库

1. **添加新的文档加载器**：
支持PDF、Word等格式的文档

2. **改进向量检索**：
- 使用更好的embedding模型
- 添加混合检索（BM25 + 向量检索）
- 实现重排序机制

3. **添加实时更新**：
支持动态添加和更新知识库内容

### 性能优化

1. **缓存机制**：
- 缓存常用查询结果
- 缓存向量计算结果

2. **并发处理**：
- 支持多用户并发访问
- 异步处理长时间任务

3. **资源优化**：
- 模型量化减少内存占用
- 向量库压缩存储

## 总结

本项目运行指南详细介绍了商家智能助手系统的：
- ✅ 完整的安装和运行流程
- ✅ 详细的功能使用说明  
- ✅ 常见错误的解决方案
- ✅ 知识库扩展方法
- ✅ 高级使用技巧

通过遵循本指南，您可以：
1. 成功部署和运行系统
2. 充分利用各项功能  
3. 扩展和定制系统
4. 解决使用过程中的问题

如有其他问题，请参考各模块的代码注释或修改相应配置文件。