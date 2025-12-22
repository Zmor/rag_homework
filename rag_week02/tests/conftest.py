"""
测试配置文件
"""

import pytest
import sys
import os

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# pytest配置
pytest_plugins = ['pytest']