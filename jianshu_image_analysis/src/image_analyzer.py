
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def read_image(image_path):
    """兼容 Windows 中文路径的图片读取函数。"""
    image_path = Path(image_path)

    if not image_path.is_file():
        print(f"图片文件不存在：{image_path}")
        return None

    try:
        image_bytes = np.fromfile(str(image_path), dtype=np.uint8)

        if image_bytes.size == 0:
            print(f"图片文件为空：{image_path}")
            return None

        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if image is None:
            print(f"图片解码失败：{image_path}")

        return image

    except (OSError, ValueError, cv2.error) as exc:
        print(f"图片读取失败：{image_path}，原因：{exc}")
        return None


def analyze_image(path):
    """分析图像技术指标，不做人脸识别或外貌吸引力判断。"""
    path = Path(path)

    base = {
        "image_path": str(path),
        "image_exists": path.is_file(),
        "width": None,
        "height": None,
        "file_size_kb": None,
        "brightness_mean": None,
        "contrast_std": None,
        "sharpness_laplacian": None,
        "aspect_ratio": None,
        "image_status": "ok",
    }

    if not path.is_file():
        base["image_status"] = "missing"
        return base

    if path.suffix.lower() not in SUPPORTED:
        base["image_status"] = "unsupported_extension"
        return base

    # 先验证文件是否为有效图片。
    try:
        with Image.open(path) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        base["image_status"] = "unreadable"
        return base

    # 使用兼容 Windows 中文路径的读取方式。
    image = read_image(path)

    if image is None:
        base["image_status"] = "unreadable"
        return base

    try:
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        base.update({
            "width": int(width),
            "height": int(height),
            "file_size_kb": round(path.stat().st_size / 1024, 2),
            "brightness_mean": round(float(np.mean(gray)), 2),
            "contrast_std": round(float(np.std(gray)), 2),
            "sharpness_laplacian": round(
                float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2
            ),
            "aspect_ratio": round(float(width / height), 4)
            if height else None,
        })

    except (OSError, ValueError, cv2.error) as exc:
        base["image_status"] = f"error: {type(exc).__name__}"

    return base
