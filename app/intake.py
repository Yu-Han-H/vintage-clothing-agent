"""LLM 需求理解，将自然语言转化为结构化参数"""

import json
from app.llm import get_llm
from app.schemas import CustomerBody, SearchParams

SYSTEM_PROMPT = """你是古着店导购助手。从顾客的话里提取两类信息，输出 JSON：

1. body：身体数据，字段为 height_cm, weight_kg, gender, fit_preference
   - gender 取值：male / female / unisex
   - fit_preference 取值：合身 / 宽松 / oversize
2. filter：商品筛选条件，字段为 category, brand, max_price
   - category 取值：top / pants / skirt / jacket

规则：只提取顾客明确提到的字段，没提到的一律设为 null。不要编造。

示例输出：
{"body": {"height_cm": 175, "gender": "male", "fit_preference": "合身"}, "filter": {"category": "jacket", "max_price": 500}}

Your response must be a valid json object."""


def parse_customer_input(text: str) -> tuple[CustomerBody, SearchParams]:
    client = get_llm()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    data = json.loads(response.choices[0].message.content)
    body = CustomerBody(**data.get("body", {}))
    params = SearchParams(**data.get("filter", {}))

    return body, params
