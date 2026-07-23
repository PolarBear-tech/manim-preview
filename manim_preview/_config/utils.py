from typing import Any


def deep_update(old: dict[str, Any], new: dict[str, Any]) -> None:
    """
    利用递归深度更新字典
    """
    for k, v in new.items():
        # 若k在base和update里对应的值都是字典时，递归
        if k in old and isinstance(v, dict) and isinstance(old[k], dict):
            deep_update(old[k], v)  # pyright: ignore[reportUnknownArgumentType]
        else:
            # 其他的直接覆盖
            old[k] = v
