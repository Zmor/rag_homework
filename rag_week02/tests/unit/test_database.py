"""
数据库管理测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_system.database.chroma_manager import ChromaDBManager


class TestChromaDBManager:
    """ChromaDB管理器测试类"""
    
    def test_init_with_config(self):
        """测试使用配置初始化"""
        with patch('src.rag_system.database.chroma_manager.config') as mock_config:
            mock_config.database.collection_name = 'test_collection'
            mock_config.database.persist_directory = './test_db'
            
            with patch('chromadb.Client') as mock_client:
                mock_collection = Mock()
                mock_client.return_value.get_or_create_collection.return_value = mock_collection
                
                manager = ChromaDBManager()
                assert manager.collection_name == 'test_collection'
                assert manager.collection == mock_collection
    
    def test_init_with_params(self):
        """测试使用参数初始化"""
        with patch('chromadb.Client') as mock_client:
            mock_collection = Mock()
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            manager = ChromaDBManager(
                collection_name='param_collection',
                embedding_function=lambda x: x
            )
            assert manager.collection_name == 'param_collection'
    
    @patch('src.rag_system.database.chroma_manager.logger')
    def test_add_documents_success(self, mock_logger):
        """测试成功添加文档"""
        mock_collection = Mock()
        
        with patch('chromadb.Client') as mock_client:
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            manager = ChromaDBManager()
            manager.add_documents(["文档1", "文档2"])
            
            mock_collection.add.assert_called_once()
            mock_logger.info.assert_called_with("成功添加 2 个文档到集合")
    
    @patch('src.rag_system.database.chroma_manager.logger')
    def test_add_documents_empty_input(self, mock_logger):
        """测试空输入"""
        with patch('chromadb.Client'):
            manager = ChromaDBManager()
            manager.add_documents([])
            
            mock_logger.warning.assert_called_with("文档列表为空")
    
    @patch('src.rag_system.database.chroma_manager.logger')
    def test_query_success(self, mock_logger):
        """测试成功查询"""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'ids': [['id1', 'id2']],
            'documents': [['文档1', '文档2']],
            'metadatas': [[{'source': 'test'}, {'source': 'test'}]],
            'distances': [[0.1, 0.2]]
        }
        
        with patch('chromadb.Client') as mock_client:
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            manager = ChromaDBManager()
            results = manager.query("测试查询")
            
            assert len(results) == 2
            assert results[0]['document'] == '文档1'
            assert results[0]['metadata'] == {'source': 'test'}
            assert results[0]['distance'] == 0.1
    
    @patch('src.rag_system.database.chroma_manager.logger')
    def test_query_empty_input(self, mock_logger):
        """测试空查询输入"""
        with patch('chromadb.Client'):
            manager = ChromaDBManager()
            results = manager.query("")
            
            assert results == []
            mock_logger.warning.assert_called_with("查询文本为空")
    
    @patch('src.rag_system.database.chroma_manager.logger')
    def test_delete_documents_success(self, mock_logger):
        """测试成功删除文档"""
        mock_collection = Mock()
        
        with patch('chromadb.Client') as mock_client:
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            manager = ChromaDBManager()
            result = manager.delete_documents(['id1', 'id2'])
            
            assert result is True
            mock_collection.delete.assert_called_once_with(ids=['id1', 'id2'])
            mock_logger.info.assert_called_with("成功删除 2 个文档")
    
    def test_get_collection_info(self):
        """测试获取集合信息"""
        mock_collection = Mock()
        mock_collection.count.return_value = 5
        
        with patch('chromadb.Client') as mock_client:
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            manager = ChromaDBManager()
            info = manager.get_collection_info()
            
            assert info['count'] == 5
            assert info['name'] == 'rag_collection'  # 默认名称