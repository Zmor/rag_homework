#!/usr/bin/env python3
"""
RAG系统示例使用脚本
演示如何使用RAG系统进行文档摄取和查询
"""

import sys
import os

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from rag_system import RAGSystem, logger


def main():
    """主函数"""
    print("RAG系统示例演示")
    print("="*50)
    
    try:
        # 初始化RAG系统
        logger.info("正在初始化RAG系统...")
        rag_system = RAGSystem()
        logger.info("RAG系统初始化完成")
        
        # 示例文档数据
        documents = [
            "人工智能（Artificial Intelligence，AI）是指由人类制造出来的机器所表现出来的智能。通常人工智能是指通过普通计算机程序来呈现人类智能的技术。",
            "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策或预测，而无需明确编程来执行特定任务。",
            "深度学习是机器学习的一个子集，它模仿人脑的工作方式，使用神经网络来处理和学习复杂的数据模式。深度学习在图像识别、语音识别和自然语言处理等领域取得了显著成果。",
            "自然语言处理（NLP）是计算机科学和人工智能领域的一个重要方向，它致力于让计算机理解和生成人类语言。",
            "计算机视觉是一门研究如何让计算机'看'的科学，它赋予了计算机理解和解释图像和视频内容的能力。"
        ]
        
        print(f"\n准备摄取 {len(documents)} 个示例文档...")
        
        # 摄取文档
        success = rag_system.ingest_documents(documents)
        if success:
            print("✅ 文档摄取成功")
        else:
            print("❌ 文档摄取失败")
            return
        
        # 获取系统信息
        print("\n系统信息:")
        system_info = rag_system.get_system_info()
        print(f"嵌入模型: {system_info['embedding_model']}")
        print(f"重排序模型: {system_info['reranker_model']}")
        print(f"LLM模型: {system_info['llm_model']}")
        print(f"集合名称: {system_info['collection_info']['name']}")
        print(f"文档数量: {system_info['collection_info']['count']}")
        
        # 示例查询
        questions = [
            "请解释一下什么是深度学习，它与机器学习有什么关系？",
            "人工智能和机器学习有什么区别？",
            "计算机视觉主要研究什么内容？"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*50}")
            print(f"示例查询 {i}: {question}")
            print("="*50)
            
            # 执行查询（不使用重排序）
            print("\n不使用重排序:")
            result_without_rerank = rag_system.query(question, use_rerank=False)
            print(f"答案: {result_without_rerank['answer']}")
            
            # 执行查询（使用重排序）
            print(f"\n使用重排序:")
            result_with_rerank = rag_system.query(question, use_rerank=True)
            print(f"答案: {result_with_rerank['answer']}")
            
            # 显示检索到的文档信息
            print(f"\n检索到的文档数量: {len(result_with_rerank['retrieved_documents'])}")
            print(f"重排序后的文档数量: {len(result_with_rerank['reranked_documents'])}")
            
            if result_with_rerank['reranked_documents']:
                print("\n重排序结果:")
                for j, doc in enumerate(result_with_rerank['reranked_documents'], 1):
                    print(f"  {j}. 相关性得分: {doc['relevance_score']:.3f}")
                    print(f"     文档: {doc['document'][:50]}...")
        
        print(f"\n{'='*50}")
        print("示例演示完成！")
        print("="*50)
        
    except Exception as e:
        logger.error(f"示例演示过程中发生错误: {str(e)}")
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()