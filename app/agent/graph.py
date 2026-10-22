"""组装 graph"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import ShoppingState
import app.agent.nodes


def build_graph():
    builder = StateGraph(ShoppingState)

    builder.add_node("understand", app.agent.nodes.understand_node)
    builder.add_node("ask", app.agent.nodes.ask_node)
    builder.add_node("search", app.agent.nodes.search_node)
    builder.add_node("present", app.agent.nodes.present_node)
    builder.add_node("relax", app.agent.nodes.relax_node)
    builder.add_node("stop", app.agent.nodes.stop_node)

    builder.add_edge(START, "understand")
    # 追问节点的输出是直接返回给顾客的回答，不需要再继续执行其他节点，所以直接连接到 END。
    builder.add_edge("ask", END)
    builder.add_edge("present", END)
    builder.add_edge("stop", END)

    builder.add_conditional_edges(
        "understand",
        app.agent.nodes.route_after_understand,
        {"ask": "ask", "search": "search", "stop": "stop"},
    )
    builder.add_conditional_edges(
        "search",
        app.agent.nodes.route_after_search,
        {"relax": "relax", "present": "present", "stop": "stop"},
    )
    # relax 后不能直接返回 search 结点，因为这会导致放宽后找到的结果被覆盖为空，进而导致陷入循环
    # 错误循环实例：search 为空 -> relax -> search（还是原条件）-> relax
    builder.add_conditional_edges(
        "relax",
        app.agent.nodes.route_after_search,
        {"present": "present", "relax": "relax","stop": "stop"},
    )

    return builder.compile(checkpointer=MemorySaver())
