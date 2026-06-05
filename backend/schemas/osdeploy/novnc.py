"""noVNC Pydantic 模型"""
from pydantic import BaseModel


class NoVNCClient(BaseModel):
    """noVNC 客户端连接信息"""
    host: str
    username: str
    password: str
    port: str = "22"