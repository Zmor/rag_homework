"""
重排序模型测试
"""

import pytest
from unittest.mock import Mock, patch
from src.rag_system.reranker.custom_reranker import CustomReranker


class TestCustomReranker:
    """自定义重排序模型测试类"""
    
    def test_init_with_config(self):
        """测试使用配置初始化"""
        with patch('src.rag_system.reranker.custom_reranker.config') as mock_config:
            mock_config.reranker.api_key = 'test_key'
            mock_config.reranker.base_url = 'https://test.com'
            mock_config.reranker.model_name = 'test_model'
            
            reranker = CustomReranker()
            assert reranker.api_key == 'test_key'
            assert reranker.base_url == 'https://test.com'
            assert reranker.model_name == 'test_model'
    
    def test_init_with_params(self):
        """测试使用参数初始化"""
        reranker = CustomReranker(
            api_key='param_key',
            base_url='https://param.com',
            model_name='param_model'
        )
        assert reranker.api_key == 'param_key'
        assert reranker.base_url == 'https://param.com'
        assert reranker.model_name == 'param_model'
    
    def test_init_without_api_key(self):
        """测试没有API密钥时初始化失败"""
        with patch('src.rag_system.reranker.custom_reranker.config') as mock_config:
            mock_config.reranker.api_key = ''
            
            with pytest.raises(ValueError, match="API密钥不能为空"):
                CustomReranker()
    
    @patch('src.rag_system.reranker.custom_reranker.requests.post')
    @patch('src.rag_system.reranker.custom_reranker.logger')
    def test_rerank_success(self, mock_logger, mock_post):
        """测试成功重排序"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"index": 0, "relevance_score": 0.9},
                {"index": 1, "relevance_score": 0.8},
                {"index": 2, "relevance_score": 0.7}
            ]
        }
        mock_post.return_value = mock_response
        
        with patch('src.rag_system.reranker.custom_reranker.config') as mock_config:
            mock_config.reranker.api_key = 'test_key'
            
            reranker = CustomReranker()
            documents = ["文档1", "文档2", "文档3"]
            result = reranker.rerank("查询", documents, top_n=2)
            
            assert len(result) == 2
            assert result[0]['document'] == "文档1"
            assert result[0]['relevance_score'] == 0.9
            assert result[1]['document'] == "文档2"
            assert result[1]['relevance_score'] == 0.8
    
    @patch('src.rag_system.reranker.custom_reranker.logger')
    def test_rerank_empty_query(self, mock_logger):
        """测试空查询"""
        with patch('src.rag_system.reranker.custom_reranker.config') as mock_config:
            mock_config.reranker.api_key = 'test_key'
            
            reranker = CustomReranker()
            result = reranker.rerank("", ["文档1"])
            
            assert result == []
            mock_logger.warning.assert_called_with("查询文本为空")
    
    @patch('src.rag_system.reranker.custom_reranker.logger')
    def test_rerank_empty_documents(self, mock_logger):
        """测试空文档列表"""
        with patch('src.rag_system.reranker.custom_reranker.config') as mock_config:
            mock_config.reranker.api_key = 'test_key'
            
            reranker = CustomReranker()
            result = reranker.rerank("查询", [])
            
            assert result == []
            mock_logger.warning.assert_called_with("文档列表为空")
    
    @patch('src.rag_system.reranker.custom_reranker.requests.post')
    def test_rerank_api_error(self, mock_post):
        """测试API错误"""
        # 模拟API错误响应
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with patch('src.rag_system.reranker.custom_reranker.config') as mock_config:
            mock_config.reranker.api_key = 'test_key'
            
            reranker = CustomReranker()
            
            with pytest.raises(RuntimeError, match="重排序API请求失败"):
                reranker.rerank("查询", ["文档1"])