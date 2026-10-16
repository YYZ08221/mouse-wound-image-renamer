from pathlib import Path

from .utils import is_supported_image, natural_sort_key


def get_image_files(folder):
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        return []
    files = [path for path in root.iterdir() if path.is_file() and is_supported_image(path)]
    return sorted(files, key=lambda path: natural_sort_key(path.name))
