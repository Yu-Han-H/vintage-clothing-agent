"""定义 node"""

from app.intake import parse_customer_input


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


def route_after_understand(state) -> str:
    pass
