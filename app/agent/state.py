"""定义 state"""

from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages


class ShoppingState(TypedDict):
    # 对话历史
    # add_messages 是 LangGraph 内置的 reducer：默认情况下 State 更新是"新值覆盖旧值"，但消息需要追加"，用 add_messages 告诉它怎么合并。
    messages: Annotated[list, add_messages]

    # 顾客身体数据（跨轮次累积，说过一次就一直记着）
    height_cm: Optional[int]
    weight_kg: Optional[int]
    gender: Optional[str]
    fit_preference: Optional[str]

    # 商品筛选条件
    category: Optional[str]
    brand: Optional[str]
    max_price: Optional[float]

    # 流程控制与中间结果
    step_count: int  # 本轮已执行的节点数，用于 MAX_STEPS 保护
    relax_count: int  # 已放宽重筛的次数（限制最多放宽 2 次）
    last_results: list  # 最近一次查到的商品列表
    reply: str  # 本轮要返回给顾客的回答
