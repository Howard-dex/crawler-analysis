import csv
from pathlib import Path
from PIL import Image, ImageDraw
import pandas as pd

from .config import DATA_DIR, IMAGE_DIR

SAMPLE_USERS = [
    {"user_id": "demo_001", "nickname": "示例用户甲", "bio": "喜欢阅读与摄影", "image_file": "sample_01.png"},
    {"user_id": "demo_002", "nickname": "示例用户乙", "bio": "记录日常生活", "image_file": "sample_02.png"},
    {"user_id": "demo_003", "nickname": "示例用户丙", "bio": "城市漫步爱好者", "image_file": "sample_03.png"},
    {"user_id": "demo_004", "nickname": "示例用户丁", "bio": "喜欢自然风景", "image_file": "sample_04.png"},
    {"user_id": "demo_005", "nickname": "示例用户戊", "bio": "练习绘画与设计", "image_file": "sample_05.png"},
    {"user_id": "demo_006", "nickname": "示例用户己", "bio": "阅读科普文章", "image_file": "sample_06.png"},
]

def create_sample_data():
    """生成完全合成的示例用户表和抽象图片，不对应真实人物。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    with (DATA_DIR / "users.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_USERS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_USERS)

    palettes = [
        ((235, 220, 195), (80, 125, 145)),
        ((30, 42, 60), (235, 170, 90)),
        ((205, 225, 210), (70, 115, 85)),
        ((245, 235, 220), (170, 115, 95)),
        ((220, 215, 240), (110, 90, 155)),
        ((235, 235, 235), (100, 130, 170)),
    ]
    sizes = [(640, 480), (512, 512), (800, 600), (320, 480), (720, 480), (400, 400)]
    for i, ((bg, accent), size) in enumerate(zip(palettes, sizes), start=1):
        im = Image.new("RGB", size, bg)
        d = ImageDraw.Draw(im)
        w, h = size
        d.ellipse((w*0.15, h*0.12, w*0.65, h*0.82), fill=accent)
        d.rectangle((w*0.55, h*0.35, w*0.9, h*0.7), fill=tuple(max(0, c-25) for c in accent))
        d.line((0, h*0.85, w, h*0.2), fill=(255, 255, 255), width=max(2, w//100))
        d.text((12, 12), f"SYNTHETIC SAMPLE {i}", fill=(25, 25, 25))
        im.save(IMAGE_DIR / f"sample_{i:02d}.png")
    return pd.DataFrame(SAMPLE_USERS)

def load_users(path=None):
    path = Path(path) if path else DATA_DIR / "users.csv"
    if not path.exists():
        create_sample_data()
    df = pd.read_csv(path, dtype={"user_id": str})
    required = {"user_id", "nickname", "image_file"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"users.csv 缺少必要字段：{sorted(missing)}")
    df["bio"] = df["bio"].fillna("") if "bio" in df.columns else ""
    return df
