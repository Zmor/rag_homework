# RAG系统 - 集成私有Embedding模型与Chroma向量数据库

一个完整的RAG（Retrieval-Augmented Generation）系统，集成了私有Embedding模型、Chroma向量数据库、重排序模型和大语言模型。

## 功能特性

- 🧠 **私有Embedding模型**: 支持自定义嵌入模型API
- 📚 **Chroma向量数据库**: 高效的向量存储和检索
- 🔄 **重排序模型**: 提升检索结果的相关性
- 🤖 **大语言模型**: 基于上下文的智能回答生成
- 🔧 **模块化设计**: 清晰的代码结构和模块化架构
- ⚙️ **配置管理**: 环境变量配置，支持敏感信息安全管理
- 📝 **完整日志**: 详细的日志记录和错误处理
- 🧪 **全面测试**: 单元测试和集成测试覆盖

## 项目结构

```
/rag_week02/
├── src/
│   └── rag_system/
│       ├── core/                 # 核心模块
│       │   ├── config.py         # 配置管理
│       │   ├── logger.py         # 日志工具
│       │   └── rag_system.py     # 主RAG系统
│       ├── embeddings/           # 嵌入模型
│       │   └── custom_embedding.py
│       ├── database/             # 向量数据库
│       │   └── chroma_manager.py
│       ├── reranker/             # 重排序模型
│       │   └── custom_reranker.py
│       └── llm/                  # 大语言模型
│           └── custom_llm.py
├── tests/                        # 测试文件
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── conftest.py               # 测试配置
├── examples/                     # 示例脚本
│   ├── demo.py                   # 演示脚本
│   └── cli.py                    # 命令行工具
├── docs/                         # 文档
├── config/                       # 配置文件
├── logs/                         # 日志文件
├── .env.example                  # 环境变量模板
├── requirements.txt              # 依赖包
├── pyproject.toml               # 项目配置
└── README.md                    # 项目说明
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果是从Git仓库）
# git clone <repository-url>
# cd rag_system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入实际的API密钥
# 必要配置：
# EMBEDDING_API_KEY=your_embedding_api_key
# RERANKER_API_KEY=your_reranker_api_key
# LLM_API_KEY=your_llm_api_key
```

### 3. 运行示例

```bash
# 运行演示脚本
python examples/demo.py

# 或者使用命令行工具
python examples/cli.py --mode interactive
```

## 使用方法

### 基本使用

```python
from rag_system import RAGSystem

# 初始化RAG系统
rag_system = RAGSystem()

# 摄取文档
documents = [
    "人工智能是计算机科学的一个分支...",
    "机器学习是人工智能的子领域..."
]
rag_system.ingest_documents(documents)

# 查询系统
result = rag_system.query("什么是人工智能？")
print(f"答案: {result['answer']}")
```

### 高级配置

```python
from rag_system import CustomEmbedding, ChromaDBManager, CustomReranker, CustomLLM

# 自定义配置
embedding = CustomEmbedding(
    api_key="your_api_key",
    base_url="https://your-api-endpoint.com",
    model_name="your-model"
)

# 创建数据库管理器
db_manager = ChromaDBManager(
    collection_name="custom_collection",
    embedding_function=embedding.get_embeddings
)

# 自定义重排序器
reranker = CustomReranker(
    api_key="your_api_key",
    base_url="https://your-api-endpoint.com",
    model_name="your-reranker-model"
)

# 自定义LLM
llm = CustomLLM(
    api_key="your_api_key",
    base_url="https://your-api-endpoint.com",
    model_name="your-llm-model"
)
```

## 环境变量配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| EMBEDDING_API_KEY | 嵌入模型API密钥 | 必填 |
| EMBEDDING_BASE_URL | 嵌入模型API地址 | https://your-api-endpoint.com/api/inference/v1 |
| EMBEDDING_MODEL_NAME | 嵌入模型名称 | bge-large-zh-v1.5 |
| RERANKER_API_KEY | 重排序模型API密钥 | 必填 |
| RERANKER_BASE_URL | 重排序模型API地址 | https://your-api-endpoint.com/api/inference/v1 |
| RERANKER_MODEL_NAME | 重排序模型名称 | bge-reranker-v2-m3 |
| LLM_API_KEY | 大语言模型API密钥 | 必填 |
| LLM_BASE_URL | 大语言模型API地址 | https://your-api-endpoint.com/api/inference/v1 |
| LLM_MODEL_NAME | 大语言模型名称 | GLM-4.6-FP8 |
| CHROMA_COLLECTION_NAME | Chroma集合名称 | rag_collection |
| CHROMA_PERSIST_DIRECTORY | Chroma持久化目录 | ./chroma_db |
| LOG_LEVEL | 日志级别 | INFO |
| LOG_FORMAT | 日志格式 | %(asctime)s - %(name)s - %(levelname)s - %(message)s |
| LOG_FILE_PATH | 日志文件路径 | logs/rag_system.log |

## 测试

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
black src/ tests/

# 代码风格检查
flake8 src/ tests/

# 类型检查
mypy src/

# 导入排序
isort src/ tests/
```

## 命令行工具

### 交互式模式

```bash
python examples/cli.py --mode interactive
```

### 查询模式

```bash
python examples/cli.py --mode query --question "什么是人工智能？"
```

### 文档摄取模式

```bash
python examples/cli.py --mode ingest --documents doc1.txt doc2.txt
```

## API文档

### RAGSystem类

#### `__init__()`
初始化RAG系统，自动配置所有组件。

#### `ingest_documents(documents, metadatas=None, ids=None)`
摄取文档到向量数据库。

**参数:**
- `documents` (List[str]): 文档内容列表
- `metadatas` (List[Dict], 可选): 文档元数据列表
- `ids` (List[str], 可选): 文档ID列表

**返回:**
- `bool`: 是否成功摄取

#### `query(question, use_rerank=True, n_results=5, top_n=3)`
查询RAG系统。

**参数:**
- `question` (str): 查询问题
- `use_rerank` (bool): 是否使用重排序，默认True
- `n_results` (int): 初始检索结果数量，默认5
- `top_n` (int): 重排序后返回结果数量，默认3

**返回:**
- `Dict`: 包含问题、上下文、答案、检索文档和重排序文档的字典

#### `get_system_info()`
获取系统信息。

**返回:**
- `Dict`: 系统信息字典，包含模型信息和集合统计

#### `clear_database()`
清空向量数据库。

**返回:**
- `bool`: 是否成功清空

## 示例数据

系统包含以下示例文档：

1. **人工智能基础**: 介绍人工智能的基本概念
2. **机器学习**: 解释机器学习与AI的关系
3. **深度学习**: 深度学习技术的应用领域
4. **自然语言处理**: NLP在AI中的重要性
5. **计算机视觉**: 计算机视觉的研究内容

## 故障排除

### 常见问题

1. **API密钥错误**: 确保所有API密钥都已正确配置
2. **网络连接问题**: 检查API端点是否可访问
3. **ChromaDB初始化失败**: 检查持久化目录权限
4. **内存不足**: 减少批处理大小或优化文档数量

### 日志调试

查看日志文件获取详细错误信息：
```bash
tail -f logs/rag_system.log
```

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (2024-12-22)
- 🎉 初始版本发布
- ✨ 完整的RAG系统实现
- 🧪 全面的测试覆盖
- 📚 完整的文档和示例