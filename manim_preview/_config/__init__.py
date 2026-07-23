"""
对于config和log进行初始化，
其他代码都依赖于它们。
"""

from .config import get_config
from .logger import set_logger

__all__ = ["config", "logger"]

# 初始化config
config = get_config()

# 根据config初始化日志
logger = set_logger(config.config)
