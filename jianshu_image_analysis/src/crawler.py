
import csv
import hashlib
import time
from io import BytesIO
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError

from config import IMAGE_DIR, DATA_DIR, OUTPUT_DIR
PAGE_URL = "https://www.w3schools.com/html/html_images.asp"
ALLOWED_HOST = "www.w3schools.com"

USERS_CSV = DATA_DIR / "users.csv"
RESULT_CSV = OUTPUT_DIR / "crawled_images.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ImagePracticeBot/1.0)"
}

MAX_IMAGES = 20
TIMEOUT = 15


def ensure_directories():
    """确保项目目录存在。"""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_existing_users():
    """读取已有用户记录，避免覆盖原来的数据。"""
    if not USERS_CSV.exists():
        return [], set()

    with USERS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    known_files = {
        row.get("image_file", "")
        for row in rows
        if row.get("image_file")
    }
    return rows, known_files


def save_users(rows):
    """保存用户记录。"""
    fields = ["user_id", "nickname", "bio", "image_file"]

    with USERS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "user_id": row.get("user_id", ""),
                "nickname": row.get("nickname", ""),
                "bio": row.get("bio", ""),
                "image_file": row.get("image_file", ""),
            })


def get_image_urls(html, page_url):
    """提取网页中的普通图片地址。"""
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    for img in soup.find_all("img"):
        # 兼容常见的懒加载属性
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-original")
        )

        if not src:
            continue

        image_url = urljoin(page_url, src)
        parsed = urlparse(image_url)

        # 仅允许 HTTPS 且域名与指定站点一致
        if parsed.scheme != "https":
            continue

        if (parsed.hostname or "").lower() != ALLOWED_HOST.lower():
            continue

        if image_url not in urls:
            urls.append(image_url)

    return urls[:MAX_IMAGES]


def download_image(session, image_url):
    """下载并验证图片，统一保存为 PNG。"""
    response = session.get(
        image_url,
        timeout=TIMEOUT,
        headers=HEADERS,
    )
    response.raise_for_status()

    # 限制下载体积，避免误下载巨大文件
    if len(response.content) > 10 * 1024 * 1024:
        print(f"跳过：图片超过 10 MB：{image_url}")
        return None

    try:
        with Image.open(BytesIO(response.content)) as image:
            image.verify()

        # 重新打开后转换格式
        with Image.open(BytesIO(response.content)) as image:
            image = image.convert("RGB")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            png_bytes = buffer.getvalue()

    except (UnidentifiedImageError, OSError, ValueError):
        print(f"跳过：响应内容不是有效图片：{image_url}")
        return None

    digest = hashlib.sha256(png_bytes).hexdigest()[:16]
    filename = f"crawl_{digest}.png"
    output_path = IMAGE_DIR / filename

    if not output_path.exists():
        output_path.write_bytes(png_bytes)

    return filename


def main():
    ensure_directories()
    users, known_files = load_existing_users()

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        response = session.get(PAGE_URL, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"网页访问失败：{exc}")
        return

    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        print("指定网址返回的不是 HTML 网页，请填写包含 img 标签的网页地址。")
        return

    image_urls = get_image_urls(response.text, PAGE_URL)

    if not image_urls:
        print("没有找到符合条件的图片。")
        print("请检查网页地址、域名，以及图片是否由 JavaScript 动态加载。")
        return

    records = []
    next_id = len(users) + 1

    for image_url in image_urls:
        try:
            filename = download_image(session, image_url)

            if not filename:
                continue

            if filename not in known_files:
                row = {
                    "user_id": f"crawl_{next_id:04d}",
                    "nickname": f"网页样本{next_id}",
                    "bio": "经许可采集的练习图片",
                    "image_file": filename,
                }
                users.append(row)
                known_files.add(filename)
                next_id += 1

            records.append({
                "image_url": image_url,
                "image_file": filename,
                "status": "success",
            })
            print(f"已保存：{filename}")

            time.sleep(0.5)

        except (requests.RequestException, OSError, ValueError) as exc:
            print(f"图片处理失败：{image_url}；原因：{exc}")
            records.append({
                "image_url": image_url,
                "image_file": "",
                "status": f"failed: {exc}",
            })

    save_users(users)

    with RESULT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["image_url", "image_file", "status"],
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"\n采集结束，找到图片链接：{len(image_urls)} 个")
    print(f"图片记录：{RESULT_CSV}")
    print(f"用户数据：{USERS_CSV}")
    print(f"图片目录：{IMAGE_DIR}")
    print("接下来运行：python main.py")


if __name__ == "__main__":
    main()
