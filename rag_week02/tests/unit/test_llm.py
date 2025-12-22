"""
LLM模型测试
"""

import pytest
from unittest.mock import Mock, patch
from src.rag_system.llm.custom_llm import CustomLLM


class TestCustomLLM:
    """自定义大语言模型测试类"""
    
    def test_init_with_config(self):
        """测试使用配置初始化"""
        with patch('src.rag_system.llm.custom_llm.config') as mock_config:
            mock_config.llm.api_key = 'test_key'
            mock_config.llm.base_url = 'https://test.com'
            mock_config.llm.model_name = 'test_model'
            
            with patch('openai.OpenAI') as mock_openai:
                llm = CustomLLM()
                assert llm.api_key == 'test_key'
                assert llm.base_url == 'https://test.com'
                assert llm.model_name == 'test_model'
    
    def test_init_with_params(self):
        """测试使用参数初始化"""
        with patch('openai.OpenAI') as mock_openai:
            llm = CustomLLM(
                api_key='param_key',
                base_url='https://param.com',
                model_name='param_model'
            )
            assert llm.api_key == 'param_key'
            assert llm.base_url == 'https://param.com'
            assert llm.model_name == 'param_model'
    
    def test_init_without_api_key(self):
        """测试没有API密钥时初始化失败"""
        with patch('src.rag_system.llm.custom_llm.config') as mock_config:
            mock_config.llm.api_key = ''
            
            with pytest.raises(ValueError, match="API密钥不能为空"):
                CustomLLM()
    
    @patch('src.rag_system.llm.custom_llm.logger')
    def test_generate_success(self, mock_logger):
        """测试成功生成文本"""
        # 模拟OpenAI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="生成的回答"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            with patch('src.rag_system.llm.custom_llm.config') as mock_config:
                mock_config.llm.api_key = 'test_key'
                
                llm = CustomLLM()
                result = llm.generate("测试提示词")
                
                assert result == "生成的回答"
                mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.rag_system.llm.custom_llm.logger')
    def test_generate_empty_prompt(self, mock_logger):
        """测试空提示词"""
        with patch('openai.OpenAI'):
            with patch('src.rag_system.llm.custom_llm.config') as mock_config:
                mock_config.llm.api_key = 'test_key'
                
                llm = CustomLLM()
                result = llm.generate("")
                
                assert result == ""
                mock_logger.warning.assert_called_with("输入提示词为空")
    
    @patch('src.rag_system.llm.custom_llm.logger')
    def test_generate_with_context_success(self, mock_logger):
        """测试成功基于上下文生成"""
        # 模拟OpenAI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="基于上下文的回答"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            with patch('src.rag_system.llm.custom_llm.config') as mock_config:
                mock_config.llm.api_key = 'test_key'
                
                llm = CustomLLM()
                context = "这是上下文信息"
                question = "这是什么？"
                result = llm.generate_with_context(context, question)
                
                assert "基于上下文的回答" in result
                assert context in mock_client.chat.completions.create.call_args[1]['messages'][0]['content']
                assert question in mock_client.chat.completions.create.call_args[1]['messages'][0]['content']
    
    def test_generate_api_error(self):
        """测试API错误"""
        # 模拟OpenAI客户端抛出异常
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        
        with patch('openai.OpenAI', return_value=mock_client):
            with patch('src.rag_system.llm.custom_llm.config') as mock_config:
                mock_config.llm.api_key = 'test_key'
                
                llm = CustomLLM()
                
                with pytest.raises(RuntimeError, match="文本生成失败"):
                    llm.generate("测试提示词")