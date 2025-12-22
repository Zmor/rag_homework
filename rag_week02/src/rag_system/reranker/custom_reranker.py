"""
自定义重排序模型模块
提供文档重排序功能
"""

from typing import List, Dict, Optional
import requests
from ..core.logger import logger, log_function_call
from ..core.config import config


class CustomReranker:
    """自定义重排序模型类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化重排序模型客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
        """
        self.api_key = api_key or config.reranker.api_key
        self.base_url = base_url or config.reranker.base_url
        self.model_name = model_name or config.reranker.model_name
        
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        
        logger.info(f"初始化重排序模型: {self.model_name}")
    
    @log_function_call
    def rerank(self, query: str, documents: List[str], top_n: int = 3) -> List[Dict]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_n: 返回前N个结果
        
        Returns:
            重排序后的文档列表
        """
        if not query:
            logger.warning("查询文本为空")
            return []
        
        if not documents:
            logger.warning("文档列表为空")
            return []
        
        if top_n <= 0:
            logger.warning("top_n参数必须大于0")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "query": query,
                "passages": documents
            }
            
            logger.debug(f"发送重排序请求，文档数量: {len(documents)}, top_n: {top_n}")
            response = requests.post(
                f"{self.base_url}/rerank",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()["results"]
                # 按相关性得分排序并取前top_n个
                sorted_results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:top_n]
                
                reranked_docs = []
                for item in sorted_results:
                    reranked_docs.append({
                        "document": documents[item["index"]],
                        "relevance_score": item["relevance_score"]
                    })
                
                logger.info(f"重排序成功，返回 {len(reranked_docs)} 个文档")
                return reranked_docs
            else:
                logger.error(f"重排序API请求失败，状态码: {response.status_code}")
                raise RuntimeError(f"重排序API请求失败，状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("重排序请求超时")
            raise RuntimeError("重排序请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"重排序请求网络错误: {str(e)}")
            raise RuntimeError(f"重排序请求网络错误: {str(e)}") from e
        except Exception as e:
            logger.error(f"重排序过程中发生错误: {str(e)}")
            raise RuntimeError(f"重排序过程中发生错误: {str(e)}") from e
    
    def __repr__(self) -> str:
        return f"CustomReranker(model_name='{self.model_name}', base_url='{self.base_url}')"