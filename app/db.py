"""数据库配置"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True, future=True)
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    # FastAPI 依赖用：每次请求只拿一个独立 session，用完关闭，避免多用户同时调用导致运行混乱
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
