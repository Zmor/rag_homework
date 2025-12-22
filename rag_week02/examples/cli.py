#!/usr/bin/env python3
"""
RAG系统命令行接口
提供交互式的RAG系统使用界面
"""

import argparse
import sys
import os
from typing import List

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from rag_system import RAGSystem, logger


def setup_rag_system() -> RAGSystem:
    """
    初始化RAG系统
    
    Returns:
        RAGSystem实例
    """
    try:
        logger.info("正在初始化RAG系统...")
        rag_system = RAGSystem()
        logger.info("RAG系统初始化完成")
        return rag_system
    except Exception as e:
        logger.error(f"RAG系统初始化失败: {str(e)}")
        sys.exit(1)


def ingest_documents(rag_system: RAGSystem, documents: List[str]) -> bool:
    """
    摄取文档
    
    Args:
        rag_system: RAG系统实例
        documents: 文档列表
    
    Returns:
        是否成功摄取
    """
    try:
        logger.info(f"正在摄取 {len(documents)} 个文档...")
        success = rag_system.ingest_documents(documents)
        if success:
            logger.info("文档摄取完成")
        else:
            logger.error("文档摄取失败")
        return success
    except Exception as e:
        logger.error(f"文档摄取过程中发生错误: {str(e)}")
        return False


def query_system(rag_system: RAGSystem, question: str, use_rerank: bool = True) -> dict:
    """
    查询RAG系统
    
    Args:
        rag_system: RAG系统实例
        question: 问题
        use_rerank: 是否使用重排序
    
    Returns:
        查询结果
    """
    try:
        logger.info(f"正在处理问题: {question[:50]}...")
        result = rag_system.query(question, use_rerank=use_rerank)
        
        print(f"\n{'='*50}")
        print(f"问题: {result['question']}")
        print(f"{'='*50}")
        print(f"答案: {result['answer']}")
        print(f"{'='*50}")
        
        if result['retrieved_documents']:
            print(f"\n检索到的文档数量: {len(result['retrieved_documents'])}")
            
        if result['reranked_documents']:
            print(f"重排序后的文档数量: {len(result['reranked_documents'])}")
            
        return result
    except Exception as e:
        logger.error(f"查询过程中发生错误: {str(e)}")
        return {"error": str(e)}


def interactive_mode(rag_system: RAGSystem):
    """
    交互式模式
    
    Args:
        rag_system: RAG系统实例
    """
    print("\n" + "="*50)
    print("RAG系统交互式模式")
    print("="*50)
    print("命令:")
    print("  q <问题> - 查询系统")
    print("  i <文档1> | <文档2> | ... - 摄取文档")
    print("  info - 显示系统信息")
    print("  clear - 清空数据库")
    print("  exit - 退出程序")
    print("="*50)
    
    while True:
        try:
            user_input = input("\n请输入命令: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == 'exit':
                print("感谢使用RAG系统，再见！")
                break
                
            elif user_input.lower() == 'info':
                info = rag_system.get_system_info()
                print(f"\n系统信息:")
                print(f"嵌入模型: {info.get('embedding_model', '未知')}")
                print(f"重排序模型: {info.get('reranker_model', '未知')}")
                print(f"LLM模型: {info.get('llm_model', '未知')}")
                collection_info = info.get('collection_info', {})
                print(f"集合名称: {collection_info.get('name', '未知')}")
                print(f"文档数量: {collection_info.get('count', 0)}")
                
            elif user_input.lower() == 'clear':
                if input("确定要清空数据库吗？(y/N): ").lower() == 'y':
                    success = rag_system.clear_database()
                    if success:
                        print("数据库已清空")
                    else:
                        print("清空数据库失败")
                        
            elif user_input.startswith('q '):
                question = user_input[2:].strip()
                if question:
                    query_system(rag_system, question)
                else:
                    print("请输入问题内容")
                    
            elif user_input.startswith('i '):
                docs_text = user_input[2:].strip()
                if docs_text:
                    documents = [doc.strip() for doc in docs_text.split('|') if doc.strip()]
                    if documents:
                        ingest_documents(rag_system, documents)
                    else:
                        print("请输入有效的文档内容")
                else:
                    print("请输入文档内容")
            else:
                print("未知命令，请输入 'exit' 查看帮助")
                
        except KeyboardInterrupt:
            print("\n\n程序被中断，正在退出...")
            break
        except Exception as e:
            logger.error(f"交互式模式发生错误: {str(e)}")
            print(f"发生错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='RAG系统命令行工具')
    parser.add_argument('--mode', choices=['interactive', 'query', 'ingest'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--question', type=str, help='查询问题')
    parser.add_argument('--documents', nargs='+', help='要摄取的文档文件路径')
    parser.add_argument('--no-rerank', action='store_true', help='禁用重排序')
    
    args = parser.parse_args()
    
    # 初始化RAG系统
    rag_system = setup_rag_system()
    
    if args.mode == 'interactive':
        interactive_mode(rag_system)
    elif args.mode == 'query':
        if not args.question:
            print("查询模式下必须提供 --question 参数")
            sys.exit(1)
        query_system(rag_system, args.question, use_rerank=not args.no_rerank)
    elif args.mode == 'ingest':
        if not args.documents:
            print("摄取模式下必须提供 --documents 参数")
            sys.exit(1)
        
        # 读取文档文件
        documents = []
        for doc_path in args.documents:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        documents.append(content)
                    else:
                        print(f"警告: 文件 {doc_path} 为空")
            except Exception as e:
                print(f"读取文件 {doc_path} 失败: {str(e)}")
                continue
        
        if documents:
            ingest_documents(rag_system, documents)
        else:
            print("没有成功读取任何文档")
            sys.exit(1)


if __name__ == '__main__':
    main()