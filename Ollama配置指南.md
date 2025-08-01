# Ollama + Qwen模型配置指南

## 1. 安装Ollama

### Windows安装
1. 访问 [Ollama官网](https://ollama.ai/) 下载Windows安装包
2. 运行安装程序，按提示完成安装
3. 安装完成后，Ollama会自动启动服务

### 验证安装
```bash
ollama --version
```

## 2. 下载和配置Qwen模型

### 下载Qwen2.5模型（推荐）
```bash
# 7B模型（推荐，平衡性能和资源消耗）
ollama pull qwen2.5:7b

# 14B模型（更强性能，需要更多内存）  
ollama pull qwen2.5:14b

# 1.5B模型（轻量级，适合低配机器）
ollama pull qwen2.5:1.5b
```

### 测试模型
```bash
# 测试对话
ollama run qwen2.5:7b

# 测试中文对话
# 输入：你好，请介绍一下自己
# 应该能正常回复中文内容
```

## 3. 配置系统使用真实LLM

### 方法1：修改配置文件
编辑 `merchant-assistant/config.py`：
```python
# 设置为生产模式
Config.set_production_mode()

# 或直接修改默认配置
DEFAULT_LLM = "ollama_qwen"  # 使用Qwen模型
DEFAULT_EMBEDDING = "sentence_transformers"  # 使用真实embedding
```

### 方法2：环境变量配置
```bash
# Windows命令行
set LLM_TYPE=ollama_qwen
set EMBEDDING_TYPE=sentence_transformers

# 然后启动系统
cd merchant-assistant
python start.py
```

### 方法3：在Web界面选择
- 启动Web界面后，在左侧边栏可以选择"Ollama模式"
- 输入模型名称：`qwen2.5:7b`
- 服务地址：`http://localhost:11434`

## 4. 系统要求

### 硬件要求
- **7B模型**：至少8GB RAM，推荐16GB
- **14B模型**：至少16GB RAM，推荐32GB
- **1.5B模型**：4GB RAM即可

### 性能对比
| 模型 | 大小 | 内存需求 | 推理速度 | 智能程度 |
|------|------|----------|----------|----------|
| qwen2.5:1.5b | ~1GB | 4GB | 快 | 基础 |
| qwen2.5:7b | ~4GB | 8GB | 中等 | 良好 |
| qwen2.5:14b | ~8GB | 16GB | 较慢 | 优秀 |

## 5. 故障排除

### Ollama服务未启动
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 手动启动服务（如果需要）
ollama serve
```

### 模型下载失败
- 检查网络连接
- 尝试使用代理：`ollama pull qwen2.5:7b --proxy http://your-proxy:port`
- 或手动下载模型文件

### 内存不足
- 选择更小的模型（1.5b版本）
- 关闭其他占用内存的程序
- 考虑使用量化版本的模型

## 6. 验证配置

### 测试LLM连接
```bash
cd merchant-assistant
python -c "
from agent.agent_executor import MerchantAssistantAgent
agent = MerchantAssistantAgent()
print('LLM配置成功！')
"
```

### 运行完整测试
```bash
cd merchant-assistant
python test_fixed.py
```

### 启动Web界面
```bash
cd merchant-assistant/ui
streamlit run streamlit_app.py
```

## 7. 高级配置

### 自定义模型参数
在 `config.py` 中修改：
```python
"ollama_qwen": {
    "type": "ollama",
    "model_name": "qwen2.5:7b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,  # 调整创造性（0-1）
    "top_p": 0.9,        # 调整生成多样性
    "max_tokens": 2048,  # 最大生成长度
}
```

### 使用GPU加速
如果有NVIDIA GPU：
```bash
# 安装CUDA版本的Ollama
# 模型会自动使用GPU加速
```

## 8. 监控和日志

### 查看Ollama日志
```bash
# Windows
C:\Users\{用户名}\.ollama\logs\server.log

# 或通过命令查看状态
ollama ps  # 查看运行中的模型
```

### 系统监控
- 使用任务管理器监控内存使用
- 使用GPU-Z监控GPU使用（如有）

配置完成后，您的商家智能助手将使用真实的Qwen模型提供更智能的对话和建议！