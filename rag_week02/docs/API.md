# RAG系统API文档

## 概述

RAG系统是一个完整的检索增强生成框架，集成了私有Embedding模型、Chroma向量数据库、重排序模型和大语言模型。

## 核心模块

### RAGSystem类

主RAG系统类，提供统一的接口进行文档摄取和查询。

```python
from rag_system import RAGSystem

rag_system = RAGSystem()
```

#### 方法

##### `ingest_documents(documents, metadatas=None, ids=None)`

将文档摄取到向量数据库中。

**参数:**
- `documents` (List[str]): 要摄取的文档内容列表
- `metadatas` (List[Dict], 可选): 每个文档的元数据列表
- `ids` (List[str], 可选): 每个文档的唯一标识符列表

**返回:**
- `bool`: 摄取成功返回True，失败返回False

**示例:**
```python
documents = [
    "人工智能是计算机科学的一个分支",
    "机器学习是人工智能的子领域"
]
success = rag_system.ingest_documents(documents)
```

##### `query(question, use_rerank=True, n_results=5, top_n=3)`

查询RAG系统并获取答案。

**参数:**
- `question` (str): 用户的问题
- `use_rerank` (bool, 可选): 是否使用重排序，默认为True
- `n_results` (int, 可选): 初始检索结果数量，默认为5
- `top_n` (int, 可选): 重排序后返回的结果数量，默认为3

**返回:**
- `Dict`: 包含以下字段的字典：
  - `question`: 输入的问题
  - `context`: 用于生成答案的上下文
  - `answer`: 生成的答案
  - `retrieved_documents`: 检索到的文档列表
  - `reranked_documents`: 重排序后的文档列表（如果使用重排序）

**示例:**
```python
result = rag_system.query("什么是人工智能？")
print(f"答案: {result['answer']}")
```

##### `get_system_info()`

获取系统的配置和状态信息。

**返回:**
- `Dict`: 包含系统信息的字典：
  - `embedding_model`: 嵌入模型名称
  - `reranker_model`: 重排序模型名称
  - `llm_model`: 大语言模型名称
  - `collection_info`: 集合信息（名称、文档数量等）
  - `config`: 配置信息（敏感信息已脱敏）

**示例:**
```python
info = rag_system.get_system_info()
print(f"当前使用模型: {info['llm_model']}")
```

##### `clear_database()`

清空向量数据库中的所有文档。

**返回:**
- `bool`: 操作成功返回True，失败返回False

**示例:**
```python
success = rag_system.clear_database()
if success:
    print("数据库已清空")
```

## 组件模块

### CustomEmbedding类

自定义嵌入模型客户端。

```python
from rag_system import CustomEmbedding

embedding = CustomEmbedding(
    api_key="your_api_key",
    base_url="https://api.example.com",
    model_name="embedding-model"
)
```

#### 方法

##### `get_embeddings(texts)`

获取文本的嵌入向量。

**参数:**
- `texts` (List[str]): 文本列表

**返回:**
- `List[List[float]]`: 嵌入向量列表

**示例:**
```python
embeddings = embedding.get_embeddings(["文本1", "文本2"])
print(f"嵌入维度: {len(embeddings[0])}")
```

### ChromaDBManager类

Chroma向量数据库管理器。

```python
from rag_system import ChromaDBManager

db_manager = ChromaDBManager(
    collection_name="my_collection",
    embedding_function=embedding.get_embeddings
)
```

#### 方法

##### `add_documents(documents, metadatas=None, ids=None)`

添加文档到集合。

**参数:**
- `documents` (List[str]): 文档内容列表
- `metadatas` (List[Dict], 可选): 文档元数据列表
- `ids` (List[str], 可选): 文档ID列表

##### `query(query_text, n_results=5)`

查询相似文档。

**参数:**
- `query_text` (str): 查询文本
- `n_results` (int, 可选): 返回结果数量，默认为5

**返回:**
- `List[Dict]`: 查询结果列表，每个结果包含document、metadata和distance字段

##### `delete_documents(ids)`

删除指定ID的文档。

**参数:**
- `ids` (List[str]): 要删除的文档ID列表

**返回:**
- `bool`: 删除成功返回True，失败返回False

##### `get_collection_info()`

获取集合信息。

**返回:**
- `Dict`: 包含集合名称和文档数量的字典

### CustomReranker类

自定义重排序模型客户端。

```python
from rag_system import CustomReranker

reranker = CustomReranker(
    api_key="your_api_key",
    base_url="https://api.example.com",
    model_name="reranker-model"
)
```

#### 方法

##### `rerank(query, documents, top_n=3)`

对文档进行重排序。

**参数:**
- `query` (str): 查询文本
- `documents` (List[str]): 要重排序的文档列表
- `top_n` (int, 可选): 返回前N个结果，默认为3

**返回:**
- `List[Dict]`: 重排序结果列表，每个结果包含document和relevance_score字段

### CustomLLM类

自定义大语言模型客户端。

```python
from rag_system import CustomLLM

llm = CustomLLM(
    api_key="your_api_key",
    base_url="https://api.example.com",
    model_name="llm-model"
)
```

#### 方法

##### `generate(prompt, max_tokens=None, temperature=0.7)`

生成文本响应。

**参数:**
- `prompt` (str): 输入提示词
- `max_tokens` (int, 可选): 最大生成token数
- `temperature` (float, 可选): 生成温度参数，默认为0.7

**返回:**
- `str`: 生成的文本响应

##### `generate_with_context(context, question, max_tokens=None, temperature=0.7)`

基于上下文生成回答。

**参数:**
- `context` (str): 上下文信息
- `question` (str): 问题
- `max_tokens` (int, 可选): 最大生成token数
- `temperature` (float, 可选): 生成温度参数，默认为0.7

**返回:**
- `str`: 生成的回答

## 配置管理

### 环境变量

系统使用环境变量进行配置，支持以下变量：

- `EMBEDDING_API_KEY`: 嵌入模型API密钥
- `EMBEDDING_BASE_URL`: 嵌入模型API地址
- `EMBEDDING_MODEL_NAME`: 嵌入模型名称
- `RERANKER_API_KEY`: 重排序模型API密钥
- `RERANKER_BASE_URL`: 重排序模型API地址
- `RERANKER_MODEL_NAME`: 重排序模型名称
- `LLM_API_KEY`: 大语言模型API密钥
- `LLM_BASE_URL`: 大语言模型API地址
- `LLM_MODEL_NAME`: 大语言模型名称
- `CHROMA_COLLECTION_NAME`: Chroma集合名称
- `CHROMA_PERSIST_DIRECTORY`: Chroma持久化目录
- `LOG_LEVEL`: 日志级别
- `LOG_FORMAT`: 日志格式
- `LOG_FILE_PATH`: 日志文件路径

### 配置验证

系统初始化时会自动验证配置：

```python
from rag_system import RAGSystem

try:
    rag_system = RAGSystem()
except ValueError as e:
    print(f"配置错误: {e}")
```

## 错误处理

系统提供完整的错误处理机制：

```python
try:
    result = rag_system.query("问题")
    if "error" in result:
        print(f"查询错误: {result['error']}")
    else:
        print(f"答案: {result['answer']}")
except Exception as e:
    print(f"系统错误: {e}")
```

## 日志记录

系统使用Python标准日志模块，支持文件和控制台输出：

```python
from rag_system import logger

logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

## 性能优化建议

1. **批处理**: 尽量批量处理文档，减少API调用次数
2. **缓存**: 考虑缓存频繁查询的结果
3. **索引优化**: 根据数据特点调整向量索引参数
4. **重排序**: 合理设置重排序的top_n参数，平衡质量和速度

## 安全注意事项

1. **API密钥**: 永远不要将API密钥硬编码在代码中
2. **环境变量**: 使用环境变量管理敏感信息
3. **日志脱敏**: 日志中自动脱敏API密钥等敏感信息
4. **访问控制**: 在生产环境中实施适当的访问控制