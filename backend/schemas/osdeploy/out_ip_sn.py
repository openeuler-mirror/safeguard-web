"""OutIpSN Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class OutIpSNBase(BaseModel):
    """出口IP序列号基础模型"""
    mac_address: str = Field(..., max_length=17, description="MAC地址")
    sn: str = Field(..., max_length=100, description="序列号")


class OutIpSNCreateRequest(OutIpSNBase):
    """创建出口IP序列号请求"""
    pass


class OutIpSNUpdateRequest(BaseModel):
    """更新出口IP序列号请求"""
    sn: Optional[str] = Field(None, max_length=100, description="序列号")


class OutIpSNResponse(OutIpSNBase):
    """出口IP序列号响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True