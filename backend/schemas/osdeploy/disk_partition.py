"""磁盘分区 Pydantic 模型"""
from typing import List, Optional
from pydantic import BaseModel


class PartitionScheme(BaseModel):
    """分区方案"""
    size: str = "100%"
    fstype: str = "ext4"
    mountpoint: str = "/data"


class DiskPartitionRequest(BaseModel):
    """磁盘分区请求"""
    host: str
    username: str
    password: str
    port: str = "22"
    disk: str
    mode: str  # Global / Free
    partitions: Optional[List[PartitionScheme]] = None
