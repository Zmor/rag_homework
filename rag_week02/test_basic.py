#!/usr/bin/env python3
"""
RAG系统功能验证脚本
"""

import sys
import os

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_basic_functionality():
    """测试基本功能"""
    print("正在测试RAG系统基本功能...")
    
    try:
        # 测试配置加载
        from rag_system.core.config import ConfigManager
        config = ConfigManager()
        print("✓ 配置管理器初始化成功")
        
        # 测试日志系统
        from rag_system.core.logger import logger
        logger.info("测试日志系统")
        print("✓ 日志系统工作正常")
        
        # 测试各个组件的导入
        from rag_system.embeddings import CustomEmbedding
        print("✓ 嵌入模型模块导入成功")
        
        from rag_system.database import ChromaDBManager
        print("✓ 数据库管理模块导入成功")
        
        from rag_system.reranker import CustomReranker
        print("✓ 重排序模块导入成功")
        
        from rag_system.llm import CustomLLM
        print("✓ 大语言模型模块导入成功")
        
        from rag_system import RAGSystem
        print("✓ 主RAG系统模块导入成功")
        
        print("\n基本功能测试通过！🎉")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_mock_components():
    """测试模拟组件"""
    print("\n正在测试模拟组件...")
    
    try:
        from unittest.mock import Mock, patch
        from rag_system.core.config import EmbeddingConfig
        
        # 测试配置类
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = 'test_value'
            config = EmbeddingConfig.from_env()
            print("✓ 配置类测试通过")
        
        print("✓ 模拟组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 模拟组件测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("RAG系统功能验证")
    print("=" * 50)
    
    success = True
    
    # 运行基本功能测试
    if not test_basic_functionality():
        success = False
    
    # 运行模拟组件测试
    if not test_mock_components():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("所有测试通过！✅")
        print("\n您现在可以:")
        print("1. 编辑 .env 文件配置API密钥")
        print("2. 运行 python examples/demo.py 体验完整功能")
        print("3. 运行 python examples/cli.py --mode interactive 使用交互式界面")
    else:
        print("部分测试失败 ❌")
        print("请检查错误信息并修复问题")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())