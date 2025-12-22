"""
日志工具模块
提供统一的日志记录功能
"""

import logging
import os
from datetime import datetime
from typing import Optional
from .config import config


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        format_string: 日志格式
    
    Returns:
        配置好的日志记录器
    """
    # 使用配置中的默认值
    if level is None:
        level = config.logging.level
    if log_file is None:
        log_file = config.logging.file_path
    if format_string is None:
        format_string = config.logging.format
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 如果日志记录器已经有处理器，先清除它们
    logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # 创建文件处理器
    if log_file:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
    
    # 创建格式化器
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    if log_file:
        file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    if log_file:
        logger.addHandler(file_handler)
    
    return logger


# 创建默认的日志记录器
logger = setup_logger('rag_system')


def log_function_call(func):
    """
    函数调用日志装饰器
    
    Args:
        func: 被装饰的函数
    
    Returns:
        包装后的函数
    """
    def wrapper(*args, **kwargs):
        logger.debug(f"调用函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise
    
    return wrapper