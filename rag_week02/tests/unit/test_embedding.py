"""
嵌入模型测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_system.embeddings.custom_embedding import CustomEmbedding


class TestCustomEmbedding:
    """自定义嵌入模型测试类"""
    
    def test_init_with_config(self):
        """测试使用配置初始化"""
        with patch('src.rag_system.embeddings.custom_embedding.config') as mock_config:
            mock_config.embedding.api_key = 'test_key'
            mock_config.embedding.base_url = 'https://test.com'
            mock_config.embedding.model_name = 'test_model'
            
            with patch('openai.OpenAI') as mock_openai:
                embedding = CustomEmbedding()
                assert embedding.api_key == 'test_key'
                assert embedding.base_url == 'https://test.com'
                assert embedding.model_name == 'test_model'
    
    def test_init_with_params(self):
        """测试使用参数初始化"""
        with patch('openai.OpenAI') as mock_openai:
            embedding = CustomEmbedding(
                api_key='param_key',
                base_url='https://param.com',
                model_name='param_model'
            )
            assert embedding.api_key == 'param_key'
            assert embedding.base_url == 'https://param.com'
            assert embedding.model_name == 'param_model'
    
    def test_init_without_api_key(self):
        """测试没有API密钥时初始化失败"""
        with patch('src.rag_system.embeddings.custom_embedding.config') as mock_config:
            mock_config.embedding.api_key = ''
            
            with pytest.raises(ValueError, match="API密钥不能为空"):
                CustomEmbedding()
    
    @patch('src.rag_system.embeddings.custom_embedding.logger')
    def test_get_embeddings_success(self, mock_logger):
        """测试成功获取嵌入向量"""
        # 模拟OpenAI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            with patch('src.rag_system.embeddings.custom_embedding.config') as mock_config:
                mock_config.embedding.api_key = 'test_key'
                
                embedding = CustomEmbedding()
                result = embedding.get_embeddings(["文本1", "文本2"])
                
                assert len(result) == 2
                assert result[0] == [0.1, 0.2, 0.3]
                assert result[1] == [0.4, 0.5, 0.6]
    
    @patch('src.rag_system.embeddings.custom_embedding.logger')
    def test_get_embeddings_empty_input(self, mock_logger):
        """测试空输入"""
        with patch('openai.OpenAI'):
            with patch('src.rag_system.embeddings.custom_embedding.config') as mock_config:
                mock_config.embedding.api_key = 'test_key'
                
                embedding = CustomEmbedding()
                result = embedding.get_embeddings([])
                
                assert result == []
                mock_logger.warning.assert_called_with("输入文本列表为空")
    
    @patch('src.rag_system.embeddings.custom_embedding.logger')
    def test_get_embeddings_api_error(self, mock_logger):
        """测试API错误"""
        # 模拟OpenAI客户端抛出异常
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API错误")
        
        with patch('openai.OpenAI', return_value=mock_client):
            with patch('src.rag_system.embeddings.custom_embedding.config') as mock_config:
                mock_config.embedding.api_key = 'test_key'
                
                embedding = CustomEmbedding()
                
                with pytest.raises(RuntimeError, match="获取嵌入向量失败"):
                    embedding.get_embeddings(["文本1"])
                
                mock_logger.error.assert_called()