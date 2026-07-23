"""
启动manim编译被监听的文件，输出视频结果，
交由显示模块处理。
"""

from pathlib import Path
from shutil import copyfile
from subprocess import PIPE, Popen
from threading import Lock
from time import sleep
from typing import Literal

from manim_preview import config, logger
from manim_preview.utils import DONE, ERROR, RENDERING, AtomicStatusContainer

# 通过锁使渲染唯一
# 渲染互斥锁
_render_lock = Lock()

# 记录程序的状态
_status = AtomicStatusContainer()


def _find_dir_name(flag: Literal["-ql", "-qm", "-qh", "-qp", "-qk"]):
    """
    由于manim输出的视频存储路径的文件夹名由视频质量决定，要找到对应的文件夹，
    必须知道这个参数，这个函数提供寻找功能。
    """
    f = {
        "-ql": "480p15",
        "-qm": "720p60",
        "-qh": "1080p60",
        "-qp": "1440p60",
        "-qk": "2160p60",
    }
    return f[flag]


def process(src_path: str, scene_name: str) -> bool:
    # 尝试获取渲染锁，拿不到直接返回，不排队
    acquired = _render_lock.acquire(blocking=False)
    if not acquired:
        logger.debug("已有任务，渲染失败。")
        return False

    log_content = ""
    success = False
    src = Path(src_path)
    try:
        # 准备开启渲染
        _status.start_render()
        _status.set_status(RENDERING)
        # 准备manim的命令行参数
        output_dir = src.parent / "media"
        quality_flag = config["manim"]["quality"]
        args = [
            "manim",
            quality_flag,
            "--media_dir",
            str(output_dir),
            src_path,
            scene_name,
        ]
        proc = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
        # 获得运行结果
        stdout, stderr = proc.communicate()
        log_content = stdout + "\n" + stderr
        # 处理运行结果
        if proc.returncode == 0:
            # 渲染成功
            success = True
            # 再将preview.mp4生成的视频复制为生成的视频
            file_name = src.stem
            dir_name = _find_dir_name(quality_flag)
            result_path = (
                output_dir / "videos" / file_name / dir_name / f"{scene_name}.mp4"
            )
            # 为了和前端保持一致，这里只能把这个文件夹写死
            tmp_output_dir = Path("./output")
            tmp_mp4_path = tmp_output_dir / "tmp.mp4"
            # 确保static文件夹存在
            tmp_output_dir.mkdir(parents=True, exist_ok=True)
            # 将渲染的文件copy到output文件夹
            copyfile(result_path, tmp_mp4_path)
            _status.set_status(DONE)
            # 留出足够的时间，让前端能够识别到status变更成Done
            # 如果留出时间，这个状态可能无法被识别，以至于新文件不会被load
            # 这个0.5s是否是最佳时间，不知道
            sleep(0.5)
        else:
            # 渲染失败
            success = False
            _status.set_status(ERROR)
            _status.add_log(log_content)
    except Exception as e:
        _status.set_status(ERROR)
        _status.add_log(str(e))
    finally:
        # 无论成功失败，一定释放锁
        _render_lock.release()
        s = _status.get_status()
        if s == DONE:
            logger.info(f"文件{src}中的{scene_name}已渲染完成。")
        elif s == ERROR:
            logger.error(f"渲染异常，异常信息：\n,{log_content}")
        # 重置渲染标记
        _status.reset()
    return success


def get_status():
    return _status.get_all()
