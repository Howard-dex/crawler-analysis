from pathlib import Path
import argparse
import pandas as pd
            
from src.config import DATA_DIR, OUTPUT_DIR, IMAGE_DIR
from src.data_loader import load_users, create_sample_data
from src.image_analyzer import analyze_image
from src.report import save_reports

def main():
    parser = argparse.ArgumentParser(description="简书图片数据分析：现代化示例项目")
    parser.add_argument("--init-sample", action="store_true", help="重新生成合成示例用户数据和图片")
    args = parser.parse_args()

    if args.init_sample or not (DATA_DIR / "users.csv").exists():
        create_sample_data()

    users = load_users()
    records = []
    for _, user in users.iterrows():                                                                                               
        image_path = IMAGE_DIR / str(user["image_file"])
        result = analyze_image(image_path)
        records.append({**user.to_dict(), **result})

    result_df = pd.DataFrame(records)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUTPUT_DIR / "image_analysis.csv", index=False, encoding="utf-8-sig")
    save_reports(result_df, OUTPUT_DIR)
    print(f"分析完成：{len(result_df)} 条示例记录")
    print(f"结果目录：{OUTPUT_DIR.resolve()}")
    print("注意：图像指标是清晰度、亮度、尺寸等客观技术指标，不是颜值评分。")

if __name__ == "__main__":
    main()
                                                                                                     