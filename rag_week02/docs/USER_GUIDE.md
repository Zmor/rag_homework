# 用户指南

## 概述

本指南将帮助您快速上手使用RAG系统，从基础安装到高级配置。

## 安装和配置

### 系统要求

- Python 3.8 或更高版本
- 稳定的网络连接（用于API调用）
- 足够的磁盘空间（用于向量数据库存储）

### 安装步骤

1. **下载项目**
   ```bash
   git clone <repository-url>
   cd rag_system
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # Windows: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入API密钥
   ```

### 获取API密钥

您需要从模型提供商处获取以下API密钥：

1. **嵌入模型API密钥** - 用于文本向量化
2. **重排序模型API密钥** - 用于文档重排序
3. **大语言模型API密钥** - 用于生成回答

## 基本使用

### 快速开始

运行演示脚本体验系统功能：

```bash
python examples/demo.py
```

### 命令行工具

使用交互式命令行工具：

```bash
python examples/cli.py --mode interactive
```

### Python API

在您的代码中使用RAG系统：

```python
from rag_system import RAGSystem

# 初始化系统
rag = RAGSystem()

# 准备文档
documents = [
    "您的文档内容1",
    "您的文档内容2"
]

# 摄取文档
rag.ingest_documents(documents)

# 查询问题
result = rag.query("您的问题")
print(result['answer'])
```

## 高级用法

### 自定义配置

#### 使用不同的模型

```python
from rag_system import CustomEmbedding, CustomReranker, CustomLLM

# 自定义嵌入模型
embedding = CustomEmbedding(
    api_key="your_key",
    base_url="https://api.example.com",
    model_name="custom-embedding-model"
)

# 自定义重排序模型
reranker = CustomReranker(
    api_key="your_key", 
    base_url="https://api.example.com",
    model_name="custom-reranker-model"
)

# 自定义LLM
llm = CustomLLM(
    api_key="your_key",
    base_url="https://api.example.com", 
    model_name="custom-llm-model"
)
```

#### 配置数据库

```python
from rag_system import ChromaDBManager

# 自定义数据库配置
db_manager = ChromaDBManager(
    collection_name="my_collection",
    embedding_function=embedding.get_embeddings
)
```

### 批量处理

```python
# 批量摄取文档
large_documents = ["doc1", "doc2", "doc3", ...]
rag.ingest_documents(large_documents)

# 批量查询
questions = ["问题1", "问题2", "问题3"]
for question in questions:
    result = rag.query(question)
    print(f"Q: {question}")
    print(f"A: {result['answer']}")
```

### 性能调优

#### 调整检索参数

```python
# 增加检索结果数量
result = rag.query(
    question="您的问题",
    n_results=10,      # 检索更多文档
    top_n=5           # 使用更多文档生成答案
)
```

#### 控制重排序

```python
# 禁用重排序以提高速度
result = rag.query(
    question="您的问题",
    use_rerank=False   # 禁用重排序
)
```

## 实际应用案例

### 知识库问答

构建企业内部知识库：

```python
# 读取知识库文档
knowledge_docs = []
for file in os.listdir("knowledge_base"):
    with open(f"knowledge_base/{file}", "r", encoding="utf-8") as f:
        knowledge_docs.append(f.read())

# 摄取知识库
rag.ingest_documents(knowledge_docs)

# 员工查询
while True:
    question = input("请输入问题 (输入'退出'结束): ")
    if question.lower() == "退出":
        break
    
    result = rag.query(question)
    print(f"答案: {result['answer']}")
```

### 文档摘要

```python
# 摄取长文档
with open("long_document.txt", "r", encoding="utf-8") as f:
    document = f.read()

# 将长文档分割成段落
paragraphs = document.split("\n\n")
rag.ingest_documents(paragraphs)

# 生成摘要
summary_query = "请总结这份文档的主要内容"
result = rag.query(summary_query)
print(result['answer'])
```

### 多轮对话

```python
conversation_history = []

while True:
    user_input = input("用户: ")
    if user_input.lower() == "退出":
        break
    
    # 构建包含历史记录的查询
    context = "\n".join([f"用户: {q}\n助手: {a}" for q, a in conversation_history])
    full_query = f"历史对话:\n{context}\n\n当前问题: {user_input}"
    
    result = rag.query(full_query)
    print(f"助手: {result['answer']}")
    
    # 更新历史记录
    conversation_history.append((user_input, result['answer']))
    
    # 保持历史记录在合理长度
    if len(conversation_history) > 5:
        conversation_history.pop(0)
```

## 故障排除

### 常见问题

#### 1. API连接失败

**症状**: 程序报错连接API失败

**解决方案**:
- 检查网络连接
- 验证API密钥是否正确
- 确认API端点地址
- 检查API配额是否用完

#### 2. 查询结果不准确

**症状**: 返回的答案与问题不相关

**解决方案**:
- 增加检索文档数量 (`n_results`)
- 调整重排序参数 (`top_n`)
- 检查文档质量
- 尝试不同的问题表述

#### 3. 系统响应慢

**症状**: 查询响应时间过长

**解决方案**:
- 禁用重排序 (`use_rerank=False`)
- 减少检索文档数量
- 使用更快的模型
- 优化网络连接

#### 4. 内存使用过高

**症状**: 程序占用过多内存

**解决方案**:
- 分批处理大文档
- 定期清理数据库
- 使用流式处理
- 调整向量维度

### 调试技巧

#### 查看详细日志

```python
import logging
from rag_system import logger

# 设置调试级别
logger.setLevel(logging.DEBUG)

# 执行操作查看详细日志
result = rag.query("测试问题")
```

#### 检查系统状态

```python
# 获取系统信息
info = rag.get_system_info()
print(f"模型信息: {info}")

# 检查数据库状态
collection_info = info['collection_info']
print(f"文档数量: {collection_info['count']}")
```

#### 验证配置

```python
from rag_system import config

# 检查配置（敏感信息已脱敏）
print(config.to_dict())
```

## 最佳实践

### 1. 文档准备

- **分段处理**: 将长文档分割成合适大小的段落
- **清理格式**: 移除无关的格式和特殊字符
- **标准化**: 统一文本编码和格式

### 2. 查询优化

- **明确问题**: 使用清晰、具体的问题
- **关键词**: 在问题中包含重要关键词
- **上下文**: 提供必要的背景信息

### 3. 性能优化

- **批处理**: 批量处理多个文档
- **缓存**: 缓存频繁查询的结果
- **索引**: 定期优化向量索引

### 4. 错误处理

- **异常捕获**: 妥善处理API异常
- **重试机制**: 实现失败重试逻辑
- **降级方案**: 准备备选方案

### 5. 监控和维护

- **日志记录**: 记录关键操作和错误
- **性能监控**: 监控响应时间和资源使用
- **定期维护**: 清理过期数据和优化性能

## 安全和隐私

### API密钥管理

- 使用环境变量存储密钥
- 定期轮换API密钥
- 限制密钥权限

### 数据保护

- 加密敏感数据
- 实施访问控制
- 定期备份重要数据

### 合规性

- 遵守数据保护法规
- 获得必要的授权
- 记录数据处理活动

## 获取更多帮助

- 查看API文档: `docs/API.md`
- 运行测试: `pytest tests/`
- 查看示例: `examples/`
- 提交问题: GitHub Issues

## 更新和支持

关注项目更新和新功能发布：
- 订阅项目通知
- 参与社区讨论
- 贡献代码和改进建议