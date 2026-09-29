"""
批量导入商品数据
=================

读取 data/products.csv，把每件商品的三类信息导入 MySQL：
  1. products     商品主表
  2. measurements 尺寸表
  3. images       图片表（自动扫描 static/images/ 目录）

设计特点（也是工程上的通用做法）：
  - 幂等：脚本可重复执行，已存在的记录自动跳过，不会重复插入
  - 事务：全部成功才 commit，中途出错自动 rollback，不会只导一半
  - 图片与数据解耦：CSV 不写图片路径，脚本按 "sku_序号.jpg" 规则自动匹配

运行方式（在项目根目录）：
  python -m scripts.import_products
"""

import csv
import os

from app.db import SessionLocal
from app.models import Product, Measurement, Image

# 项目内的固定路径
CSV_PATH = os.path.join("data", "products.csv")
IMAGES_DIR = os.path.join("static", "images")


# ---------- 小工具函数 ----------


def parse_int(value: str):
    """CSV 里读出来的都是字符串，转成整数；空字符串表示没有值，返回 None"""
    value = value.strip()
    return int(value) if value else None


def parse_str(value: str):
    """字符串字段：去掉首尾空格，空字符串统一转成 None"""
    value = value.strip()
    return value if value else None


# ---------- 核心：导入一件商品 ----------


def import_one_row(db, row: dict):
    """处理 CSV 中的一行（一件商品的完整信息）"""
    sku = row["sku"].strip()

    # 第 1 步：商品主表 —— 已存在则跳过
    product = db.query(Product).filter(Product.sku == sku).first()
    if product is None:
        db.add(
            Product(
                sku=sku,
                category=parse_str(row["category"]),
                gender=parse_str(row["gender"]),
                brand=parse_str(row["brand"]),
                price=float(row["price"].strip()) if row["price"].strip() else None,
                condition=parse_str(row["condition"]),
                source_platform=parse_str(row["source_platform"]),
                description=parse_str(row["description"]),
            )
        )
        # flush：立刻把商品 INSERT 进数据库（但还没 commit）。
        # 这样下面插尺寸/图片时，外键就能在 products 表里找到这件商品。
        db.flush()
        print(f"  [+] 新增商品 {sku}")
    else:
        print(f"  [=] 商品 {sku} 已存在，跳过")

    # 第 2 步：尺寸表 —— 已存在则跳过
    measurement = db.query(Measurement).filter(Measurement.sku == sku).first()
    if measurement is None:
        db.add(
            Measurement(
                sku=sku,
                chest_cm=parse_int(row["chest_cm"]),
                shoulder_cm=parse_int(row["shoulder_cm"]),
                length_cm=parse_int(row["length_cm"]),
                sleeve_cm=parse_int(row["sleeve_cm"]),
                waist_cm=parse_int(row["waist_cm"]),
                hip_cm=parse_int(row["hip_cm"]),
            )
        )
        print(f"  [+] 新增尺寸 {sku}")
    else:
        print(f"  [=] 尺寸 {sku} 已存在，跳过")

    # 第 3 步：图片表 —— 扫描 static/images/，找以 "sku_" 开头的文件
    if not os.path.isdir(IMAGES_DIR):
        return

    for filename in sorted(os.listdir(IMAGES_DIR)):
        # 关键：前缀必须是 "sku_"，所以 S298_ 不会误匹配到 S298XXL_
        if not filename.startswith(f"{sku}_"):
            continue

        url = f"/static/images/{filename}"
        if db.query(Image).filter(Image.url == url).first():
            continue  # 这张图已经录过了

        # 从文件名 H264_1.jpg 里取出序号 1 作为 sort_order
        sort_order = 0
        number_part = filename.rsplit("_", 1)[-1].split(".")[0]
        if number_part.isdigit():
            sort_order = int(number_part)

        db.add(Image(sku=sku, url=url, sort_order=sort_order))
        print(f"  [+] 新增图片 {url}")


# ---------- 入口 ----------


def main():
    print(f"读取 CSV：{CSV_PATH}\n")

    db = SessionLocal()
    try:
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)  # 按表头把每行读成字典
            total = 0
            for row in reader:
                total += 1
                print(f"({total}) 处理商品 {row['sku'].strip()}")
                import_one_row(db, row)

        db.commit()  # 全部成功，一次性提交
        print(f"\n导入完成，共处理 {total} 件商品")

    except Exception as e:
        db.rollback()  # 任何一步出错，撤销本次所有改动
        print(f"\n导入失败，已回滚：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
