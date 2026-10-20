# 简书交友图片项目：Python 现代化重构示例

当前版本是**可运行的教学重构骨架**，使用合成用户记录和抽象示例图片，不抓取真实用户，不做人脸识别或外貌吸引力评分。

## 环境

- Python 3.11 或 3.12
- VS Code
- 建议使用虚拟环境

## 安装

Windows PowerShell：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

如果 PowerShell 不允许激活虚拟环境，也可以直接运行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 运行

在项目根目录运行：

```powershell
python main.py --init-sample
```

输出包括：

- `outputs/image_analysis.csv`：逐张图片的技术指标
- `outputs/summary_statistics.csv`：数值指标描述统计
- `outputs/status_counts.csv`：图片处理状态统计
- `outputs/brightness_by_user.png`：亮度对比图
- `outputs/image_dimensions.png`：尺寸散点图

运行测试：

```powershell
pytest -q
```

## 使用自己的图片

1. 将你有权使用的图片放到 `data/images/`。
2. 编辑 `data/users.csv`，字段至少包括 `user_id,nickname,image_file`，`bio` 可选。
3. `image_file` 填图片文件名。
4. 执行 `python main.py`。

## 当前实现的指标

- 宽度、高度、文件大小
- 灰度平均亮度
- 灰度标准差（粗略反映对比度）
- 拉普拉斯方差（常用的清晰度启发式指标）
- 宽高比
- 文件缺失、格式不支持等状态

这些指标受图像内容、设备和拍摄条件影响，不代表人物外貌、人格或社会价值。

## 如何接入合法的数据采集

目前没有启用网络爬虫。若要加入数据采集，建议单独新增 `src/crawler.py`，仅访问允许自动化访问的页面或官方 API，遵守网站服务条款、robots.txt、速率限制及版权/隐私要求；不绕过登录、验证码、访问控制或反爬机制。下载前应核验图片使用权限，并设置超时、重试、缓存与请求间隔。

## 与原项目的差异

要准确复刻原项目，必须取得原仓库源文件。当前无法仅凭项目名称确定其请求 URL、页面解析规则、图片保存逻辑、第三方评分模型、评分权重、预处理方法、依赖版本和结果图表。因此本仓库是现代化重构的可运行起点，不声称已复现原项目的具体评分算法。
