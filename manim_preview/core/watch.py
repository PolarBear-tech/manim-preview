from pathlib import Path
from threading import Timer
from typing import override

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from manim_preview import config, logger

from .process import process


class _ManimAniFileHandler(FileSystemEventHandler):
    def __init__(self, src_path: str, scene_name: str) -> None:
        self.src_path: str = src_path
        self.scene_name: str = scene_name
        self.interval: float = config["manim"]["render_interval"]
        self.tasks: dict[Path, Timer] = {}

    @override
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        # 事件触发的目标路径
        triggered = Path(event.src_path)  # pyright: ignore[reportArgumentType]
        target = Path(self.src_path)

        # 去除非目标事件
        if triggered != target:
            logger.debug(f"非目标监听事件{triggered}")

        # 能够保证triggered和target是同一个目标，只用target即可
        # 添加防抖去重机制
        if target in self.tasks:
            previous = self.tasks[target]
            previous.cancel()
            logger.debug(f"{target}被重复编译，{previous}已取消")

        present = Timer(self.interval, process, [self.src_path, self.scene_name])
        present.start()
        self.tasks[target] = present
        logger.debug(f"检测到{target}被修改，创建{present}，{self.interval}s后开始编译")


def start_watch(src_path: str, scene_name: str):
    running = False
    target = Path(src_path)
    # 得到脚本文件所在父级文件路径，因为Observer只能监听文件的父级文件夹
    target_dir = str(target.parent)
    handler = _ManimAniFileHandler(src_path, scene_name)
    observer = Observer()

    observer.schedule(handler, target_dir, recursive=False)
    observer.start()
    logger.debug(f"已开启{target_dir}的监听。")

    # 开启循环
    try:
        running = True
        while running:
            pass
    except KeyboardInterrupt as e:
        logger.error(str(e))
        observer.stop()
        # 最终需要全部取消计时器
        for timer in handler.tasks.values():
            timer.cancel()
    observer.stop()
