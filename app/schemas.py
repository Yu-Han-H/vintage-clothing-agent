"""使用 Pydantic 模型设计数据结构"""

from typing import Optional
from pydantic import BaseModel


# 顾客身体数据
class CustomerBody(BaseModel):
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    gender: Optional[str] = None
    fit_preference: Optional[str] = None


# 结构化筛选参数，便于查询
class SearchParams(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None

    chest_min: Optional[int] = None
    chest_max: Optional[int] = None

    length_min: Optional[int] = None
    length_max: Optional[int] = None

    max_price: Optional[float] = None
