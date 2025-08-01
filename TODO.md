# 🧠 商家智能助手系统 —— 全流程开发路线图

## 🚩 项目阶段总览

| 阶段 | 目标 |
|------|------|
| 第 1 阶段 | 环境准备 + 复现 Langchain-Chatchat |
| 第 2 阶段 | 构建商家助手知识库 + Prompt 重构 |
| 第 3 阶段 | 接入内容生成 + 推荐策略工具 |
| 第 4 阶段 | 构建 Agent 流程 + 多轮控制逻辑 |
| 第 5 阶段 | 加入效果评估模块（CTR / 关键词） |
| 第 6 阶段 | 模块化抽象 + UI 界面集成 |
| 第 7 阶段 | 测试优化 + 总结交付 |

---

## ✅ 第 1 阶段：复现 Langchain‑Chatchat

### 🔧 环境准备

```bash
# 克隆仓库
git clone https://github.com/chatchat-space/langchain-chatchat.git
cd langchain-chatchat
```
# 建议使用 conda 虚拟环境
conda create -n chatchat python=3.10
conda activate chatchat

# 安装依赖
pip install -r requirements.txt


### 🚀 跑通基础系统

1. 启动向量数据库（支持 FAISS / Milvus）；
2. 构建本地知识库：将测试文档放入路径：
3. 向量化构建：
```bash
python cli/knowledge_vector.py --filepath "docs/test"
```
4. 启动服务：
```bash
python startup.py
```
5. 打开 Web UI：
```bash
http://localhost:7860
```
## ✅ 第 2 阶段：构建商家助手知识库

### 📦 文档内容建议

- 商家运营指南（策略优化、选品技巧）
- 商品内容模板（优秀标题、描述、关键词）
- 平台活动说明（京东618、抖音投放技巧等）

将这些文档放入路径：

```bash
./knowledge/docs/merchant/
```

## ✅ 第 3 阶段：添加商家工具（Tool）

### 🛠 示例 Tool 编写

文件：/agent/tools/merchant_tools.py
```bash
from langchain.tools import tool

@tool
def generate_product_title(product_info: str) -> str:
    """根据商品信息生成推荐标题"""
    return f"【夏日爆款】{product_info}，限时特惠"

@tool
def suggest_strategy(product_type: str) -> str:
    """根据商品类目返回推荐策略"""
    return f"推荐参与618活动，关键词：清凉/简约/爆款"
```

### ✅ 注册工具
文件：/agent/agent_executor.py
```bash
from agent.tools.merchant_tools import generate_product_title, suggest_strategy

tools = [
    generate_product_title,
    suggest_strategy,
    # 其他工具
]
```

##  ✅第 4 阶段：构建 Agent 流程
### 🤖 Prompt 示例（策略生成）
```bash
你是一个电商运营顾问助手，帮助商家完成商品内容优化与投放策略建议。
请根据提供的商品信息，生成商品标题和对应的推荐策略。
商品信息：连衣裙，粉色，夏季，价格 129 元
```

### 🧠 多轮控制建议（可选）
- 使用 Langchain memory 模块存储上下文；

- 控制执行顺序：RAG → Tool → 生成 → 评估；

- 添加“是否要优化策略？”等追问逻辑。

##  ✅ 第 5 阶段：加入效果评估模块
### 🔍 CTR 评分函数示例（关键词覆盖率）
文件：/agent/tools/merchant_tools.py
```bash
@tool
def estimate_ctr(title: str, keywords: list) -> float:
    """估算标题点击率得分：关键词覆盖率作为近似指标"""
    count = sum([1 for kw in keywords if kw in title])
    return round(count / len(keywords), 2)
```
### ✅ 示例调用
```bash
estimate_ctr("夏季新款女装 清凉显瘦", ["夏季", "连衣裙", "清凉", "新款"])
# 返回 0.75
```

## ✅ 第 6 阶段：模块化抽象 + UI 整合

### 📦 模块结构建议

| 模块             | 功能说明                                   |
|------------------|--------------------------------------------|
| 文案生成模块     | Prompt 编排 + LLM 生成文案                  |
| 策略推荐模块     | 检索历史策略 + LLM 输出新策略               |
| 工具执行模块     | 注册并管理工具（Tool）执行                  |
| CTR 评估模块     | 简单模型 / 函数对候选策略进行打分           |
| Agent 控制器     | 管理任务分流、多轮交互、上下文记忆等控制逻辑 |

---

### 🌐 可选 UI 界面（推荐使用）

#### ✅ 修改 Langchain-Chatchat 自带 UI：

- 添加“商家助手模式”入口
- 增加“生成标题”/“生成策略”按钮
- 输出区域增加标题、策略、CTR 估分展示区

#### ✅ 或使用 Streamlit 构建轻量 Web 页面：

```text
[商品输入区域]
      ↓
[点击生成按钮]
      ↓
[输出区域]
    - 推荐标题
    - 推荐策略
    - CTR 模拟得分
```

## ✅ 第 7 阶段：测试优化 + 项目总结

### ✅ 测试清单

| 模块         | 测试内容                                 |
|--------------|------------------------------------------|
| 知识库       | 是否能成功检索对应策略文档               |
| 内容生成     | 是否能输出符合意图的标题                 |
| Tool 调用    | 是否能按需触发对应函数                   |
| Agent 流程   | 多轮调用是否逻辑合理，结果是否有效提升   |
| UI           | 操作流程是否顺畅，交互是否友好           |

---

### 🎁 项目交付说明

建议交付以下材料：

- ✅ 项目说明文档（README）：
  - 项目背景  
  - 技术架构图  
  - 模块功能说明  
  - 安装与运行方式  
  - 示例截图或演示页面链接  

- ✅ 可选交付内容：
  - 演示视频（推荐上传至 bilibili 或 YouTube）
  - 在线部署链接（如 Streamlit Cloud / HuggingFace Spaces）
  - GitHub 项目链接（含开源许可证）

---

### 📌 补充建议（选做优化）

- ✅ 引入 BM25 + embedding 的 hybrid 检索机制，提高检索准确率；
- ✅ 使用 ChatGLM3-int4、Mistral 等小模型，进行模型量化部署，提升推理效率；
- ✅ 设计对比实验：比较生成策略与历史策略在 CTR 或转化率上的预估效果；
- ✅ 构建多商家、多类目的测试数据集，提高系统的泛化能力。
