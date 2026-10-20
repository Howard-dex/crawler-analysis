from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def save_reports(df: pd.DataFrame, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    numeric = df.select_dtypes(include="number")
    numeric.describe().T.to_csv(output_dir / "summary_statistics.csv", encoding="utf-8-sig")
    status = df["image_status"].value_counts(dropna=False)
    status.rename_axis("image_status").reset_index(name="count").to_csv(
        output_dir / "status_counts.csv", index=False, encoding="utf-8-sig"
    )

    if "brightness_mean" in df.columns:
        plot_df = df.dropna(subset=["brightness_mean"])
        if not plot_df.empty:
            plt.figure(figsize=(9, 5))
            plt.bar(plot_df["nickname"].astype(str), plot_df["brightness_mean"])
            plt.title("Image Brightness by Synthetic User")
            plt.xlabel("Synthetic user")
            plt.ylabel("Mean grayscale brightness (0-255)")
            plt.xticks(rotation=25, ha="right")
            plt.tight_layout()
            plt.savefig(output_dir / "brightness_by_user.png", dpi=150)
            plt.close()

    if {"width", "height"}.issubset(df.columns):
        plot_df = df.dropna(subset=["width", "height"])
        if not plot_df.empty:
            plt.figure(figsize=(7, 5))
            plt.scatter(plot_df["width"], plot_df["height"])
            plt.title("Image Dimensions")
            plt.xlabel("Width (pixels)")
            plt.ylabel("Height (pixels)")
            plt.tight_layout()
            plt.savefig(output_dir / "image_dimensions.png", dpi=150)
            plt.close()
