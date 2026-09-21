"""将用户数据转换为商品数据的匹配范围"""

from app.schemas import CustomerBody, SearchParams


def body_to_search_params(body: CustomerBody, category: str = None) -> SearchParams:
    if not body.height_cm:
        return SearchParams(category=category)

    h = body.height_cm

    # 衣长（后衣长）约为身高0.38~0.43倍
    length_min = int(h * 0.38)
    length_max = int(h * 0.43)

    # 处理胸围
    if body.gender == "female":
        base_chest = h - 85
    else:
        base_chest = h - 80

    # 依据用户或商品版型风格对尺寸进行调整，没明确就默认6cm
    fit_add = {"合身": 4, "宽松": 8, "oversize": 12}.get(body.fit_preference, 6)

    chest_min = base_chest + fit_add - 3
    chest_max = base_chest + fit_add + 5

    return SearchParams(
        category=category,
        chest_min=chest_min,
        chest_max=chest_max,
        length_min=length_min,
        length_max=length_max,
    )
