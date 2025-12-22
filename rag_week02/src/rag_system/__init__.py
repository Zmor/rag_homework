"""
RAG系统主模块
提供统一的导入接口
"""

from .core import RAGSystem, config, logger
from .embeddings import CustomEmbedding
from .database import ChromaDBManager
from .reranker import CustomReranker
from .llm import CustomLLM

__all__ = [
    'RAGSystem',
    'CustomEmbedding', 
    'ChromaDBManager',
    'CustomReranker',
    'CustomLLM',
    'config',
    'logger'
]

__version__ = "1.0.0"