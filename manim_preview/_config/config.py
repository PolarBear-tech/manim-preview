"""
初始化config，
可配置条目都有哪些，详见当前文件下的配置文件或README.md的"## 可配置项"
"""

from pathlib import Path
from tomllib import load
from typing import Any, override

from .utils import deep_update

# config文件的名字
_CONFIG_FILE_NAME = "mpconfig.toml"


class _Config:
    """
    储存所有的可变配置，
    目前只包括当前文件夹下的配置文件和程序运行时所在cwd的配置文件
    """

    def __init__(self) -> None:
        # 用于储存各种配置
        self.config: dict[str, Any] = {}

    def read(self, config: dict[str, Any]) -> None:
        deep_update(self.config, config)

    @override
    def __str__(self) -> str:
        return str(self.config)

    def __getitem__(self, item: str) -> Any:
        return self.config[item]


def get_config() -> _Config:
    """
    为外部提供得到config的api
    """
    config = _Config()
    # 默认的配置文件在当前文件夹下
    default = Path(__file__).parent / _CONFIG_FILE_NAME
    with default.open("rb") as df:
        config.read(load(df))
    # 用户的配置文件在程序运行的cwd下的同级文件夹下
    user = Path(f"./{_CONFIG_FILE_NAME}")
    # 有可能不存在
    if user.exists():
        with user.open("rb") as ur:
            config.read(load(ur))
    return config
