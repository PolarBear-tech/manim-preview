import sys
from typing import Any

from loguru import logger


def set_logger(config: dict[str, Any]):
    logger.remove()
    formatter = config["log"]["console_formatter"]
    # 控制台输出
    logger.add(
        sys.stderr,
        level=config["log"]["console_level"],
        format=formatter,
        colorize=True,
    )
    # 文件输出
    # 好吧，这里把rotation和retention都写死，每天0点创建新的日志文件，保存15天
    logger.add(
        sink=config["log"]["file_sink"],
        level=config["log"]["file_level"],
        rotation="00:00",
        retention=15,
        format=formatter,
    )
    return logger
