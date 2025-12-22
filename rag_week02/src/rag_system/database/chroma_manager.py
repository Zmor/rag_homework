"""
ChromaDB数据库管理模块
提供向量数据库的增删改查功能
"""

from typing import List, Dict, Optional, Callable
import chromadb
from chromadb.config import Settings
from ..core.logger import logger, log_function_call
from ..core.config import config


class ChromaDBManager:
    """ChromaDB管理器"""
    
    def __init__(self, collection_name: Optional[str] = None, embedding_function: Optional[Callable] = None):
        """
        初始化ChromaDB管理器
        
        Args:
            collection_name: 集合名称
            embedding_function: 嵌入函数
        """
        self.collection_name = collection_name or config.database.collection_name
        self.embedding_function = embedding_function
        
        # 配置ChromaDB客户端
        chroma_settings = Settings()
        if config.database.persist_directory:
            chroma_settings.persist_directory = config.database.persist_directory
        
        self.client = chromadb.Client(settings=chroma_settings)
        self.collection = self._get_or_create_collection()
        
        logger.info(f"初始化ChromaDB管理器，集合名称: {self.collection_name}")
    
    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"使用现有集合: {self.collection_name}")
        except Exception:
            # 如果集合不存在，创建新集合
            collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"创建新集合: {self.collection_name}")
        
        return collection
    
    @log_function_call
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        """
        添加文档到集合
        
        Args:
            documents: 文档内容列表
            metadatas: 文档元数据列表
            ids: 文档ID列表
        """
        if not documents:
            logger.warning("文档列表为空")
            return
        
        # 自动生成元数据和ID（如果未提供）
        if metadatas is None:
            metadatas = [{"source": "default"} for _ in documents]
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        try:
            # 如果有嵌入函数，先生成嵌入向量
            if self.embedding_function:
                embeddings = self.embedding_function(documents)
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            else:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            logger.info(f"成功添加 {len(documents)} 个文档到集合")
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise RuntimeError(f"添加文档失败: {str(e)}") from e
    
    @log_function_call
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        查询相似文档
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
        
        Returns:
            查询结果列表
        """
        if not query_text:
            logger.warning("查询文本为空")
            return []
        
        try:
            # 如果有嵌入函数，先生成查询向量
            if self.embedding_function:
                query_embedding = self.embedding_function([query_text])[0]
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
            else:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
            
            formatted_results = []
            if results['ids'][0]:  # 检查是否有结果
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            logger.info(f"查询成功，返回 {len(formatted_results)} 个结果")
            return formatted_results
            
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise RuntimeError(f"查询失败: {str(e)}") from e
    
    @log_function_call
    def delete_documents(self, ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            ids: 要删除的文档ID列表
        
        Returns:
            是否删除成功
        """
        if not ids:
            logger.warning("文档ID列表为空")
            return False
        
        try:
            self.collection.delete(ids=ids)
            logger.info(f"成功删除 {len(ids)} 个文档")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict:
        """获取集合信息"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "persist_directory": config.database.persist_directory
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {str(e)}")
            return {"name": self.collection_name, "count": 0, "error": str(e)}
    
    def __repr__(self) -> str:
        return f"ChromaDBManager(collection_name='{self.collection_name}')"