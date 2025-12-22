"""
配置文件管理模块
管理RAG系统的所有配置项，包括API密钥、模型参数等
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class EmbeddingConfig:
    """嵌入模型配置"""
    api_key: str
    base_url: str
    model_name: str
    
    @classmethod
    def from_env(cls) -> 'EmbeddingConfig':
        """从环境变量创建配置"""
        return cls(
            api_key=os.getenv('EMBEDDING_API_KEY', ''),
            base_url=os.getenv('EMBEDDING_BASE_URL', '/api/inference/v1'),
            model_name=os.getenv('EMBEDDING_MODEL_NAME', 'bge-large-zh-v1.5')
        )


@dataclass
class RerankerConfig:
    """重排序模型配置"""
    api_key: str
    base_url: str
    model_name: str
    
    @classmethod
    def from_env(cls) -> 'RerankerConfig':
        """从环境变量创建配置"""
        return cls(
            api_key=os.getenv('RERANKER_API_KEY', ''),
            base_url=os.getenv('RERANKER_BASE_URL', '/api/inference/v1'),
            model_name=os.getenv('RERANKER_MODEL_NAME', 'bge-reranker-v2-m3')
        )


@dataclass
class LLMConfig:
    """大语言模型配置"""
    api_key: str
    base_url: str
    model_name: str
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """从环境变量创建配置"""
        return cls(
            api_key=os.getenv('LLM_API_KEY', ''),
            base_url=os.getenv('LLM_BASE_URL', '/api/inference/v1'),
            model_name=os.getenv('LLM_MODEL_NAME', 'GLM-4.6-FP8')
        )


@dataclass
class DatabaseConfig:
    """数据库配置"""
    collection_name: str
    persist_directory: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量创建配置"""
        return cls(
            collection_name=os.getenv('CHROMA_COLLECTION_NAME', 'rag_collection'),
            persist_directory=os.getenv('CHROMA_PERSIST_DIRECTORY', None)
        )


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str
    format: str
    file_path: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """从环境变量创建配置"""
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=os.getenv('LOG_FILE_PATH', 'logs/rag_system.log')
        )


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.embedding = EmbeddingConfig.from_env()
        self.reranker = RerankerConfig.from_env()
        self.llm = LLMConfig.from_env()
        self.database = DatabaseConfig.from_env()
        self.logging = LoggingConfig.from_env()
    
    def validate_config(self) -> bool:
        """验证配置是否完整"""
        required_keys = [
            self.embedding.api_key,
            self.reranker.api_key,
            self.llm.api_key
        ]
        
        if not all(required_keys):
            missing_configs = []
            if not self.embedding.api_key:
                missing_configs.append("EMBEDDING_API_KEY")
            if not self.reranker.api_key:
                missing_configs.append("RERANKER_API_KEY")
            if not self.llm.api_key:
                missing_configs.append("LLM_API_KEY")
            
            raise ValueError(f"缺少必需的API密钥配置: {', '.join(missing_configs)}")
        
        return True
    
    def to_dict(self) -> dict:
        """将配置转换为字典"""
        return {
            'embedding': {
                'api_key': '***' if self.embedding.api_key else '',
                'base_url': self.embedding.base_url,
                'model_name': self.embedding.model_name
            },
            'reranker': {
                'api_key': '***' if self.reranker.api_key else '',
                'base_url': self.reranker.base_url,
                'model_name': self.reranker.model_name
            },
            'llm': {
                'api_key': '***' if self.llm.api_key else '',
                'base_url': self.llm.base_url,
                'model_name': self.llm.model_name
            },
            'database': {
                'collection_name': self.database.collection_name,
                'persist_directory': self.database.persist_directory
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_path': self.logging.file_path
            }
        }


# 全局配置实例
config = ConfigManager()