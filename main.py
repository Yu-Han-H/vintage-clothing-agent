"""完成 FastAPI 接口设计"""

import uuid

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.agent.graph import build_graph

graph = build_graph()

app = FastAPI(title="古着导购 agent")

app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    thread_id: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 没传 thread_id 就生成新的
    thread_id = req.thread_id or str(uuid.uuid4())

    result = graph.invoke(
        {"messages": [HumanMessage(content=req.message)]},
        {"configurable": {"thread_id": thread_id}},
    )
    return ChatResponse(reply=result["messages"][-1].content, thread_id=thread_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
