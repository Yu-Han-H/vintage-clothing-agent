"""完成 FastAPI 接口设计"""

import uuid
import os

from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from sqlalchemy import func

from app.agent.graph import build_graph
from app.db import SessionLocal
from app.models import Image, Product

graph = build_graph()

app = FastAPI(title="古着导购 agent")

app.mount("/static", StaticFiles(directory="static"), name="static")

IMAGES_DIR = "static/images"
ALLOWED_EXT = {".jpg", ".jpeg", ".png"}


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    thread_id: str
    image: list[str] = []


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 没传 thread_id 就生成新的
    thread_id = req.thread_id or str(uuid.uuid4())

    result = graph.invoke(
        {"messages": [HumanMessage(content=req.message)]},
        {"configurable": {"thread_id": thread_id}},
    )
    return ChatResponse(reply=result["messages"][-1].content, thread_id=thread_id)


@app.post("/upload")
def upload_image(sku: str = Form(...), file: UploadFile = File(...)):
    # sku 必须存在于 products 表
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            raise HTTPException(404, detail=f"商品 {sku} 不存在")

        # 扩展名白名单
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(400, detail="仅支持 jpg/jpeg/png 格式")

        # 序号 = 库中该 sku 最大 sort_order + 1（查库，不扫文件夹）
        last = db.query(func.max(Image.sort_order)).filter(Image.sku == sku).scalar()
        next_num = (last or 0) + 1
        filename = f"{sku}_{next_num}{ext}"
        save_path = os.path.join(IMAGES_DIR, filename)

        # 保存文件（二进制写入）
        content = file.file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        # 写数据库
        url = f"/static/images/{filename}"
        db.add(Image(sku=sku, url=url, sort_order=next_num))
        db.commit()

        return {"url": url, "filename": filename, "sort_order": next_num}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
