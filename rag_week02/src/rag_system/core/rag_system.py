"""
RAG系统主框架模块
集成嵌入、检索、重排序和生成功能的完整RAG系统
"""

import uuid
from typing import List, Dict, Optional, Any
from ..embeddings.custom_embedding import CustomEmbedding
from ..database.chroma_manager import ChromaDBManager
from ..reranker.custom_reranker import CustomReranker
from ..llm.custom_llm import CustomLLM
from ..core.logger import logger, log_function_call
from ..core.config import config


class RAGSystem:
    """RAG系统主类"""
    
    def __init__(self):
        """初始化RAG系统"""
        logger.info("正在初始化RAG系统...")
        
        # 验证配置
        config.validate_config()
        
        # 初始化各个组件
        self.embedding_client = CustomEmbedding()
        self.db_manager = ChromaDBManager(embedding_function=self.embedding_client.get_embeddings)
        self.reranker = CustomReranker()
        self.llm_client = CustomLLM()
        
        logger.info("RAG系统初始化完成")
    
    @log_function_call
    def ingest_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None) -> bool:
        """
        摄取文档到向量数据库
        
        Args:
            documents: 文档内容列表
            metadatas: 文档元数据列表
            ids: 文档ID列表
        
        Returns:
            是否成功摄取
        """
        if not documents:
            logger.warning("文档列表为空")
            return False
        
        try:
            # 自动生成元数据和ID（如果未提供）
            if metadatas is None:
                metadatas = [{"source": "default"} for _ in documents]
            
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # 获取文档的嵌入向量
            embeddings = self.embedding_client.get_embeddings(documents)
            
            if not embeddings:
                logger.error("文档嵌入失败")
                return False
            
            # 将文档添加到向量数据库
            self.db_manager.add_documents(documents, metadatas, ids)
            
            logger.info(f"成功摄取 {len(documents)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"文档摄取失败: {str(e)}")
            return False
    
    @log_function_call
    def query(self, question: str, use_rerank: bool = True, n_results: int = 5, top_n: int = 3) -> Dict[str, Any]:
        """
        查询RAG系统
        
        Args:
            question: 问题
            use_rerank: 是否使用重排序
            n_results: 初始检索结果数量
            top_n: 重排序后返回的结果数量
        
        Returns:
            包含问题、上下文和答案的字典
        """
        if not question:
            logger.warning("问题为空")
            return {
                "question": question,
                "context": "",
                "answer": "问题不能为空",
                "retrieved_documents": [],
                "reranked_documents": []
            }
        
        try:
            logger.info(f"正在处理问题: {question[:50]}...")
            
            # 步骤1：检索相关文档
            retrieved_docs = self.db_manager.query(question, n_results=n_results)
            
            if not retrieved_docs:
                logger.warning("未检索到相关文档")
                return {
                    "question": question,
                    "context": "",
                    "answer": "抱歉，未找到相关的上下文信息来回答您的问题。",
                    "retrieved_documents": [],
                    "reranked_documents": []
                }
            
            logger.info(f"检索到 {len(retrieved_docs)} 个相关文档")
            
            # 步骤2：如果启用重排序，对文档进行重排序
            if use_rerank:
                doc_texts = [doc["document"] for doc in retrieved_docs]
                reranked_docs = self.reranker.rerank(question, doc_texts, top_n=top_n)
                
                if reranked_docs:
                    context = "\n".join([doc["document"] for doc in reranked_docs])
                    logger.info(f"重排序后选择 {len(reranked_docs)} 个文档作为上下文")
                else:
                    # 如果重排序失败，使用原始检索结果
                    context = "\n".join([doc["document"] for doc in retrieved_docs[:top_n]])
                    logger.warning("重排序失败，使用原始检索结果")
                    reranked_docs = []
            else:
                # 不使用重排序，直接使用检索结果
                context = "\n".join([doc["document"] for doc in retrieved_docs[:top_n]])
                reranked_docs = []
                logger.info(f"使用原始检索结果，选择 {top_n} 个文档作为上下文")
            
            # 步骤3：使用LLM生成回答
            answer = self.llm_client.generate_with_context(context, question)
            
            result = {
                "question": question,
                "context": context,
                "answer": answer,
                "retrieved_documents": retrieved_docs,
                "reranked_documents": reranked_docs
            }
            
            logger.info("问题处理完成")
            return result
            
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            return {
                "question": question,
                "context": "",
                "answer": f"处理问题时发生错误: {str(e)}",
                "retrieved_documents": [],
                "reranked_documents": []
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            系统信息字典
        """
        try:
            collection_info = self.db_manager.get_collection_info()
            
            return {
                "embedding_model": self.embedding_client.model_name,
                "reranker_model": self.reranker.model_name,
                "llm_model": self.llm_client.model_name,
                "collection_info": collection_info,
                "config": config.to_dict()
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return {"error": str(e)}
    
    def clear_database(self) -> bool:
        """
        清空数据库
        
        Returns:
            是否成功清空
        """
        try:
            # 获取所有文档ID
            collection_info = self.db_manager.get_collection_info()
            if collection_info["count"] > 0:
                # 这里需要实现获取所有文档ID的逻辑
                # 由于ChromaDB的限制，我们重新创建集合
                import chromadb
                self.db_manager.client.delete_collection(name=config.database.collection_name)
                self.db_manager = ChromaDBManager(embedding_function=self.embedding_client.get_embeddings)
                logger.info("数据库已清空")
            else:
                logger.info("数据库已经是空的")
            
            return True
        except Exception as e:
            logger.error(f"清空数据库失败: {str(e)}")
            return False
    
    def __repr__(self) -> str:
        return f"RAGSystem(embedding_model='{self.embedding_client.model_name}', llm_model='{self.llm_client.model_name}')"