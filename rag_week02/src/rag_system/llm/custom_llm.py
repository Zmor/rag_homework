"""
自定义大语言模型模块
提供文本生成功能
"""

from typing import Optional
from openai import OpenAI
from ..core.logger import logger, log_function_call
from ..core.config import config


class CustomLLM:
    """自定义大语言模型类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化大语言模型客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
        """
        self.api_key = api_key or config.llm.api_key
        self.base_url = base_url or config.llm.base_url
        self.model_name = model_name or config.llm.model_name
        
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        
        # 延迟初始化客户端，避免测试时的问题
        self._client = None
        logger.info(f"初始化大语言模型: {self.model_name}")
    
    @property
    def client(self):
        """延迟加载客户端"""
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client
    
    @log_function_call
    def generate(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            temperature: 生成温度参数
        
        Returns:
            生成的文本响应
        """
        if not prompt:
            logger.warning("输入提示词为空")
            return ""
        
        try:
            logger.debug(f"正在生成文本，模型: {self.model_name}, 温度: {temperature}")
            
            messages = [{"role": "user", "content": prompt}]
            
            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**request_params)
            
            result = response.choices[0].message.content
            logger.debug(f"文本生成成功，长度: {len(result)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise RuntimeError(f"文本生成失败: {str(e)}") from e
    
    @log_function_call
    def generate_with_context(self, context: str, question: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> str:
        """
        基于上下文生成回答
        
        Args:
            context: 上下文信息
            question: 问题
            max_tokens: 最大生成token数
            temperature: 生成温度参数
        
        Returns:
            生成的回答
        """
        if not context and not question:
            logger.warning("上下文和问题都为空")
            return ""
        
        # 构建RAG提示词模板
        prompt = f"""基于以下上下文回答问题：

上下文：
{context}

问题：{question}

请根据上下文回答问题。如果上下文中没有相关信息，请说明无法基于提供的上下文回答问题。"""
        
        return self.generate(prompt, max_tokens, temperature)
    
    def __repr__(self) -> str:
        return f"CustomLLM(model_name='{self.model_name}', base_url='{self.base_url}')"