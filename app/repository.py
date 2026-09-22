"""商品查询"""

from sqlalchemy.orm import Session
from app.models import Product, Measurement, Image
from app.schemas import SearchParams


# 按参数筛选商品，返回包含尺寸与图片 URL 的列表
def search_products(db: Session, params: SearchParams) -> list[dict]:
    query = db.query(Product).join(Measurement, Product.sku == Measurement.sku)

    if params.category:
        query = query.filter(Product.category == params.category)
    if params.brand:
        query = query.filter(Product.brand == params.brand)

    if params.chest_min is not None:
        query = query.filter(Measurement.chest_cm >= params.chest_min)
    if params.chest_max is not None:
        query = query.filter(Measurement.chest_cm <= params.chest_max)

    if params.length_min is not None:
        query = query.filter(Measurement.length_cm >= params.length_min)
    if params.length_max is not None:
        query = query.filter(Measurement.length_cm <= params.length_max)

    if params.max_price:
        query = query.filter(Product.price <= params.max_price)

    products = query.all()
    results = []

    for p in products:
        m = db.query(Measurement).filter(Measurement.sku == p.sku).first()
        images = (
            db.query(Image).filter(Image.sku == p.sku).order_by(Image.sort_order).all()
        )
        results.append(
            {
                "sku": p.sku,
                "brand": p.brand,
                "category": p.category,
                "price": float(p.price) if p.price else None,
                "description": p.description,
                "chest_cm": m.chest_cm if m else None,
                "length_cm": m.length_cm if m else None,
                "sleeve_cm": m.sleeve_cm if m else None,
                "images": [img.url for img in images],
            }
        )
    return results
