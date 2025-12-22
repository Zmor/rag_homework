# 运行测试脚本

import pytest
import sys
import os

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

if __name__ == "__main__":
    # 运行所有测试
    exit_code = pytest.main(["-v", "--tb=short"])
    sys.exit(exit_code)