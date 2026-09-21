"""
建立 ORM 模型：将数据库中的表映射为 Python 类
相较于传统的 SQL 查询，ORM 提供了更高层次的抽象，可以使用面向对象的方式来操作数据库，避免手写 SQL 命令和表记录，从而提高开发效率和代码可读性
"""

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DECIMAL,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from app.db import Base


# 商品表
class Product(Base):
    __tablename__ = "products"

    sku = Column(String(32), primary_key=True)
    category = Column(
        String(20), nullable=False, comment="品类: top/pants/skirt/jacket"
    )
    gender = Column(String(10), comment="male/female/unisex")
    brand = Column(String(64))
    price = Column(DECIMAL(10, 2))
    condition = Column(String(20), comment="new/like_new/good")
    source_platform = Column(String(20))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


# 商品尺寸表
class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False)
    chest_cm = Column(Integer)
    shoulder_cm = Column(Integer)
    length_cm = Column(Integer, comment="外套存后衣长")
    sleeve_cm = Column(Integer)
    waist_cm = Column(Integer)
    hip_cm = Column(Integer)


# 商品图片表
class Image(Base):
    __tablename__ = "images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False)
    url = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)


# 顾客表
class Customer(Base):
    __tablename__ = "customers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    gender = Column(String(10))
    preference = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
