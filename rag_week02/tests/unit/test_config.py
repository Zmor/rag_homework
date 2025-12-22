"""
配置文件测试
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.rag_system.core.config import ConfigManager, EmbeddingConfig, RerankerConfig, LLMConfig


class TestConfig:
    """配置测试类"""
    
    def test_embedding_config_from_env(self):
        """测试嵌入配置从环境变量加载"""
        with patch.dict(os.environ, {
            'EMBEDDING_API_KEY': 'test_key',
            'EMBEDDING_BASE_URL': 'https://test.com',
            'EMBEDDING_MODEL_NAME': 'test_model'
        }):
            config = EmbeddingConfig.from_env()
            assert config.api_key == 'test_key'
            assert config.base_url == 'https://test.com'
            assert config.model_name == 'test_model'
    
    def test_reranker_config_from_env(self):
        """测试重排序配置从环境变量加载"""
        with patch.dict(os.environ, {
            'RERANKER_API_KEY': 'test_key',
            'RERANKER_BASE_URL': 'https://test.com',
            'RERANKER_MODEL_NAME': 'test_model'
        }):
            config = RerankerConfig.from_env()
            assert config.api_key == 'test_key'
            assert config.base_url == 'https://test.com'
            assert config.model_name == 'test_model'
    
    def test_llm_config_from_env(self):
        """测试LLM配置从环境变量加载"""
        with patch.dict(os.environ, {
            'LLM_API_KEY': 'test_key',
            'LLM_BASE_URL': 'https://test.com',
            'LLM_MODEL_NAME': 'test_model'
        }):
            config = LLMConfig.from_env()
            assert config.api_key == 'test_key'
            assert config.base_url == 'https://test.com'
            assert config.model_name == 'test_model'
    
    def test_config_manager_validate_success(self):
        """测试配置验证成功"""
        with patch.dict(os.environ, {
            'EMBEDDING_API_KEY': 'test_key',
            'RERANKER_API_KEY': 'test_key',
            'LLM_API_KEY': 'test_key'
        }):
            manager = ConfigManager()
            assert manager.validate_config() is True
    
    def test_config_manager_validate_failure(self):
        """测试配置验证失败"""
        with patch.dict(os.environ, {
            'EMBEDDING_API_KEY': '',
            'RERANKER_API_KEY': '',
            'LLM_API_KEY': ''
        }):
            manager = ConfigManager()
            with pytest.raises(ValueError, match="缺少必需的API密钥配置"):
                manager.validate_config()
    
    def test_config_to_dict(self):
        """测试配置转换为字典"""
        with patch.dict(os.environ, {
            'EMBEDDING_API_KEY': 'test_key',
            'RERANKER_API_KEY': 'test_key',
            'LLM_API_KEY': 'test_key'
        }):
            manager = ConfigManager()
            config_dict = manager.to_dict()
            
            assert 'embedding' in config_dict
            assert 'reranker' in config_dict
            assert 'llm' in config_dict
            assert 'database' in config_dict
            assert 'logging' in config_dict
            
            assert config_dict['embedding']['api_key'] == '***'
            assert config_dict['reranker']['api_key'] == '***'
            assert config_dict['llm']['api_key'] == '***'