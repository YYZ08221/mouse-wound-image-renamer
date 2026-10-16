import re
from pathlib import Path


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
ILLEGAL_CHARS = set('\\/:*?"<>|')


def natural_sort_key(value):
    text = str(value)
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text)]


def is_supported_image(path):
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def has_illegal_chars(name):
    return any(char in ILLEGAL_CHARS for char in name)


def build_target_name(user_input, original_suffix):
    name = user_input.strip()
    if not name:
        raise ValueError("新文件名不能为空")
    if has_illegal_chars(name):
        raise ValueError('文件名不能包含 Windows 禁用字符：\\ / : * ? " < > |')

    target = Path(name)
    suffix = target.suffix.lower()
    if suffix:
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的扩展名：{target.suffix}")
        return name
    return f"{name}{original_suffix}"


def safe_int(value, default, minimum=0):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, number)
