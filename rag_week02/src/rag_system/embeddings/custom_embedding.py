"""
自定义嵌入模型模块
提供文本向量化功能
"""

from typing import List, Optional
from openai import OpenAI
from ..core.logger import logger, log_function_call
from ..core.config import config


class CustomEmbedding:
    """自定义嵌入模型类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化嵌入模型客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
        """
        self.api_key = api_key or config.embedding.api_key
        self.base_url = base_url or config.embedding.base_url
        self.model_name = model_name or config.embedding.model_name
        
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        
        # 延迟初始化客户端，避免测试时的问题
        self._client = None
        logger.info(f"初始化嵌入模型: {self.model_name}")
    
    @property
    def client(self):
        """延迟加载客户端"""
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client
    
    @log_function_call
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        获取文本的嵌入向量
        
        Args:
            texts: 文本列表
        
        Returns:
            嵌入向量列表
        """
        if not texts:
            logger.warning("输入文本列表为空")
            return []
        
        try:
            logger.debug(f"正在获取 {len(texts)} 个文本的嵌入向量")
            response = self.client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"成功获取嵌入向量，维度: {len(embeddings[0]) if embeddings else 0}")
            return embeddings
        except Exception as e:
            logger.error(f"获取嵌入向量失败: {str(e)}")
            raise RuntimeError(f"获取嵌入向量失败: {str(e)}") from e
    
    def __repr__(self) -> str:
        return f"CustomEmbedding(model_name='{self.model_name}', base_url='{self.base_url}')"