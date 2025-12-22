"""
集成测试
"""

import pytest
from unittest.mock import Mock, patch
from src.rag_system.core.rag_system import RAGSystem


class TestIntegration:
    """集成测试类"""
    
    @patch('src.rag_system.core.rag_system.config')
    def test_full_rag_workflow(self, mock_config):
        """测试完整的RAG工作流程"""
        mock_config.validate_config.return_value = True
        
        # 模拟各个组件
        with patch('src.rag_system.core.rag_system.CustomEmbedding') as mock_embedding_class:
            mock_embedding = Mock()
            mock_embedding.get_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
            mock_embedding.model_name = 'test_embedding'
            mock_embedding_class.return_value = mock_embedding
            
            with patch('src.rag_system.core.rag_system.ChromaDBManager') as mock_db_class:
                mock_db = Mock()
                mock_db.query.return_value = [
                    {"document": "人工智能是计算机科学的一个分支", "metadata": {"source": "test"}, "distance": 0.1},
                    {"document": "机器学习是人工智能的子领域", "metadata": {"source": "test"}, "distance": 0.2}
                ]
                mock_db.get_collection_info.return_value = {"name": "test_collection", "count": 2}
                mock_db_class.return_value = mock_db
                
                with patch('src.rag_system.core.rag_system.CustomReranker') as mock_reranker_class:
                    mock_reranker = Mock()
                    mock_reranker.rerank.return_value = [
                        {"document": "人工智能是计算机科学的一个分支", "relevance_score": 0.95},
                        {"document": "机器学习是人工智能的子领域", "relevance_score": 0.85}
                    ]
                    mock_reranker.model_name = 'test_reranker'
                    mock_reranker_class.return_value = mock_reranker
                    
                    with patch('src.rag_system.core.rag_system.CustomLLM') as mock_llm_class:
                        mock_llm = Mock()
                        mock_llm.generate_with_context.return_value = "人工智能是计算机科学的一个重要分支，它致力于创造能够执行通常需要人类智能的任务的系统。机器学习是人工智能的一个子领域，它使计算机能够从数据中学习。"
                        mock_llm.model_name = 'test_llm'
                        mock_llm_class.return_value = mock_llm
                        
                        # 创建RAG系统并执行完整流程
                        rag_system = RAGSystem()
                        
                        # 步骤1：摄取文档
                        documents = [
                            "人工智能是计算机科学的一个分支",
                            "机器学习是人工智能的子领域",
                            "深度学习是机器学习的一种方法"
                        ]
                        
                        ingest_result = rag_system.ingest_documents(documents)
                        assert ingest_result is True
                        
                        # 步骤2：查询系统
                        question = "什么是人工智能？"
                        query_result = rag_system.query(question)
                        
                        assert query_result['question'] == question
                        assert '人工智能是计算机科学的一个分支' in query_result['context']
                        assert len(query_result['answer']) > 0
                        assert len(query_result['retrieved_documents']) == 2
                        assert len(query_result['reranked_documents']) == 2
                        
                        # 步骤3：获取系统信息
                        system_info = rag_system.get_system_info()
                        assert system_info['embedding_model'] == 'test_embedding'
                        assert system_info['reranker_model'] == 'test_reranker'
                        assert system_info['llm_model'] == 'test_llm'
                        assert system_info['collection_info']['count'] == 2
    
    @patch('src.rag_system.core.rag_system.config')
    def test_error_handling_workflow(self, mock_config):
        """测试错误处理工作流程"""
        mock_config.validate_config.return_value = True
        
        with patch('src.rag_system.core.rag_system.CustomEmbedding') as mock_embedding_class:
            mock_embedding = Mock()
            mock_embedding.get_embeddings.return_value = []
            mock_embedding_class.return_value = mock_embedding
            
            with patch('src.rag_system.core.rag_system.ChromaDBManager') as mock_db_class:
                mock_db = Mock()
                mock_db.query.return_value = []
                mock_db_class.return_value = mock_db
                
                with patch('src.rag_system.core.rag_system.CustomReranker') as mock_reranker_class:
                    mock_reranker = Mock()
                    mock_reranker.rerank.return_value = []
                    mock_reranker_class.return_value = mock_reranker
                    
                    with patch('src.rag_system.core.rag_system.CustomLLM') as mock_llm_class:
                        mock_llm = Mock()
                        mock_llm.generate_with_context.return_value = "抱歉，未找到相关的上下文信息来回答您的问题。"
                        mock_llm_class.return_value = mock_llm
                        
                        rag_system = RAGSystem()
                        
                        # 测试空文档摄取
                        result = rag_system.ingest_documents([])
                        assert result is False
                        
                        # 测试查询无结果的情况
                        query_result = rag_system.query("不相关的问题")
                        assert "未找到相关的上下文信息" in query_result['answer']
                        assert len(query_result['retrieved_documents']) == 0