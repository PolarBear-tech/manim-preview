from argparse import ArgumentParser
from webbrowser import open
from threading import Thread

from manim_preview import config, logger
from manim_preview.core import start_watch, start_server


def main():
    parser = ArgumentParser("a manim animation preview tool")

    parser.add_argument("src_path")
    parser.add_argument("scene_name")

    args = parser.parse_args()

    path: str = args.src_path
    name: str = args.scene_name
    port = config["http"]["port"]

    # 后端监听
    watch = Thread(target=start_watch, args=[path, name], daemon=True)
    watch.start()
    # 前端的服务
    server = Thread(target=start_server, args=[port], daemon=True)
    server.start()
    # 自动开启浏览器
    open(f"http://127.0.0.1:{port}")
    try:
        while True:
            pass
    except Exception as e:
        logger.error(str(e))
