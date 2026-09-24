"""单轮 workflow"""

from app.db import SessionLocal
from app.intake import parse_customer_input
from app.sizing import body_to_search_params
from app.repository import search_products


def run_single_turn(user_text: str) -> dict:
    body, params = parse_customer_input(user_text)

    if body.height_cm:
        size_params = body_to_search_params(body, category=params.category)

        params.chest_min = size_params.chest_min
        params.chest_max = size_params.chest_max
        params.length_min = size_params.length_min
        params.length_max = size_params.length_max

    db = SessionLocal()
    try:
        results = search_products(db, params)
    finally:
        db.close()

    return {
        "理解需求": {
            "身体数据": body.model_dump(),
            "筛选条件": params.model_dump(),
        },
        "匹配商品数": len(results),
        "商品列表": results,
    }
