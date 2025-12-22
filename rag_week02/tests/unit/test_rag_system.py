"""
RAG系统主框架测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_system.core.rag_system import RAGSystem


class TestRAGSystem:
    """RAG系统测试类"""
    
    @patch('src.rag_system.core.rag_system.config')
    @patch('src.rag_system.core.rag_system.CustomEmbedding')
    @patch('src.rag_system.core.rag_system.ChromaDBManager')
    @patch('src.rag_system.core.rag_system.CustomReranker')
    @patch('src.rag_system.core.rag_system.CustomLLM')
    def test_init_success(self, mock_llm, mock_reranker, mock_db, mock_embedding, mock_config):
        """测试成功初始化"""
        mock_config.validate_config.return_value = True
        
        rag_system = RAGSystem()
        
        assert rag_system.embedding_client is not None
        assert rag_system.db_manager is not None
        assert rag_system.reranker is not None
        assert rag_system.llm_client is not None
    
    @patch('src.rag_system.core.rag_system.config')
    def test_init_config_validation_failure(self, mock_config):
        """测试配置验证失败"""
        mock_config.validate_config.side_effect = ValueError("配置错误")
        
        with pytest.raises(ValueError, match="配置错误"):
            RAGSystem()
    
    @patch('src.rag_system.core.rag_system.logger')
    @patch('src.rag_system.core.rag_system.config')
    def test_ingest_documents_success(self, mock_config, mock_logger):
        """测试成功摄取文档"""
        mock_config.validate_config.return_value = True
        
        with patch('src.rag_system.core.rag_system.CustomEmbedding') as mock_embedding_class:
            mock_embedding = Mock()
            mock_embedding.get_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
            mock_embedding_class.return_value = mock_embedding
            
            with patch('src.rag_system.core.rag_system.ChromaDBManager') as mock_db_class:
                mock_db = Mock()
                mock_db_class.return_value = mock_db
                
                rag_system = RAGSystem()
                result = rag_system.ingest_documents(["文档1", "文档2"])
                
                assert result is True
                mock_db.add_documents.assert_called_once()
    
    @patch('src.rag_system.core.rag_system.logger')
    @patch('src.rag_system.core.rag_system.config')
    def test_ingest_documents_empty_input(self, mock_config, mock_logger):
        """测试空文档输入"""
        mock_config.validate_config.return_value = True
        
        with patch('src.rag_system.core.rag_system.CustomEmbedding'):
            with patch('src.rag_system.core.rag_system.ChromaDBManager'):
                rag_system = RAGSystem()
                result = rag_system.ingest_documents([])
                
                assert result is False
                mock_logger.warning.assert_called_with("文档列表为空")
    
    @patch('src.rag_system.core.rag_system.logger')
    @patch('src.rag_system.core.rag_system.config')
    def test_query_success_with_rerank(self, mock_config, mock_logger):
        """测试成功查询（使用重排序）"""
        mock_config.validate_config.return_value = True
        
        with patch('src.rag_system.core.rag_system.CustomEmbedding') as mock_embedding_class:
            mock_embedding = Mock()
            mock_embedding_class.return_value = mock_embedding
            
            with patch('src.rag_system.core.rag_system.ChromaDBManager') as mock_db_class:
                mock_db = Mock()
                mock_db.query.return_value = [
                    {"document": "文档1", "metadata": {"source": "test"}, "distance": 0.1},
                    {"document": "文档2", "metadata": {"source": "test"}, "distance": 0.2}
                ]
                mock_db_class.return_value = mock_db
                
                with patch('src.rag_system.core.rag_system.CustomReranker') as mock_reranker_class:
                    mock_reranker = Mock()
                    mock_reranker.rerank.return_value = [
                        {"document": "文档1", "relevance_score": 0.9}
                    ]
                    mock_reranker_class.return_value = mock_reranker
                    
                    with patch('src.rag_system.core.rag_system.CustomLLM') as mock_llm_class:
                        mock_llm = Mock()
                        mock_llm.generate_with_context.return_value = "生成的回答"
                        mock_llm_class.return_value = mock_llm
                        
                        rag_system = RAGSystem()
                        result = rag_system.query("测试问题")
                        
                        assert result['question'] == "测试问题"
                        assert result['answer'] == "生成的回答"
                        assert len(result['retrieved_documents']) == 2
                        assert len(result['reranked_documents']) == 1
    
    @patch('src.rag_system.core.rag_system.logger')
    @patch('src.rag_system.core.rag_system.config')
    def test_query_empty_question(self, mock_config, mock_logger):
        """测试空问题输入"""
        mock_config.validate_config.return_value = True
        
        with patch('src.rag_system.core.rag_system.CustomEmbedding'):
            with patch('src.rag_system.core.rag_system.ChromaDBManager'):
                with patch('src.rag_system.core.rag_system.CustomReranker'):
                    with patch('src.rag_system.core.rag_system.CustomLLM'):
                        rag_system = RAGSystem()
                        result = rag_system.query("")
                        
                        assert result['answer'] == "问题不能为空"
                        mock_logger.warning.assert_called_with("问题为空")
    
    @patch('src.rag_system.core.rag_system.config')
    def test_get_system_info(self, mock_config):
        """测试获取系统信息"""
        mock_config.validate_config.return_value = True
        
        with patch('src.rag_system.core.rag_system.CustomEmbedding') as mock_embedding_class:
            mock_embedding = Mock()
            mock_embedding.model_name = 'test_embedding_model'
            mock_embedding_class.return_value = mock_embedding
            
            with patch('src.rag_system.core.rag_system.ChromaDBManager') as mock_db_class:
                mock_db = Mock()
                mock_db.get_collection_info.return_value = {'name': 'test_collection', 'count': 10}
                mock_db_class.return_value = mock_db
                
                with patch('src.rag_system.core.rag_system.CustomReranker') as mock_reranker_class:
                    mock_reranker = Mock()
                    mock_reranker.model_name = 'test_reranker_model'
                    mock_reranker_class.return_value = mock_reranker
                    
                    with patch('src.rag_system.core.rag_system.CustomLLM') as mock_llm_class:
                        mock_llm = Mock()
                        mock_llm.model_name = 'test_llm_model'
                        mock_llm_class.return_value = mock_llm
                        
                        with patch('src.rag_system.core.rag_system.config') as mock_config_instance:
                            mock_config_instance.to_dict.return_value = {'test': 'config'}
                            
                            rag_system = RAGSystem()
                            info = rag_system.get_system_info()
                            
                            assert info['embedding_model'] == 'test_embedding_model'
                            assert info['reranker_model'] == 'test_reranker_model'
                            assert info['llm_model'] == 'test_llm_model'
                            assert info['collection_info']['count'] == 10