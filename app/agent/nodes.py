"""定义 node"""

from app.intake import parse_customer_input


# 理解用户输入，更新状态
def understand_node(state):
    latest_text = state["messages"][-1].content
    body, params = parse_customer_input(latest_text)

    update = {}
    if body.height_cm is not None:
        update["height_cm"] = body.height_cm
    if body.weight_kg is not None:
        update["weight_kg"] = body.weight_kg
    if body.gender is not None:
        update["gender"] = body.gender
    if body.fit_preference is not None:
        update["fit_preference"] = body.fit_preference
    if params.category is not None:
        update["category"] = params.category
    if params.brand is not None:
        update["brand"] = params.brand
    if params.max_price is not None:
        update["max_price"] = params.max_price

    update["step_count"] = state.get("step_count", 0) + 1
    return update


# 判断理解的信息是否完备，是则查库，否则追问
def route_after_understand(state) -> str:
    if not state.get("height_cm"):
        return "ask"
    if not state.get("category"):
        return "ask"
    if not state.get("gender"):
        return "ask"
    return "search"


from langchain_core.messages import AIMessage

# 规定追问话术，使回答更稳定
ASK_TEXT = {
    "height_cm": "请问您的身高",
    "category": "您想找什么类型的衣服（比如外套、上衣、裤子）",
    "gender": "请问您的性别",
}


# 追问节点
def ask_node(state):
    missing = []
    if not state.get("height_cm"):
        missing.append("height_cm")
    if not state.get("category"):
        missing.append("category")
    if not state.get("gender"):
        missing.append("gender")

    question = "".join(ASK_TEXT[field] for field in ASK_TEXT)
    text = f"为精准匹配，请补充信息：{question}"

    return {
        "reply": text,
        "messages": [AIMessage(content=text)],
    }


from app.repository import search_products
from app.schemas import SearchParams, CustomerBody
from app.sizing import body_to_search_params
from app.db import SessionLocal


# 查库节点：换算尺寸->查库->存进 state
def search_node(state):
    body = CustomerBody(
        height_cm=state.get("height_cm"),
        weight_kg=state.get("weight_kg"),
        gender=state.get("gender"),
        fit_preference=state.get("fit_preference"),
    )

    params = SearchParams(
        category=state.get("category"),
        brand=state.get("brand"),
        max_price=state.get("max_price"),
    )

    size = body_to_search_params(body, category=params.category)
    params.chest_min = size.chest_min
    params.chest_max = size.chest_max
    params.length_min = size.length_min
    params.length_max = size.length_max

    db = SessionLocal()
    try:
        results = search_products(db, params)
    finally:
        db.close()

    return {
        "last_results": results,
        "step_count": state.get("step_count", 0) + 1,
    }
