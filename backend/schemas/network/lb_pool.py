"""LBPool Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class LBPoolBase(BaseModel):
    """后端池基础模型"""
    name: str = Field(..., max_length=100, description="名称")
    loadbalancer: int = Field(..., description="负载均衡器ID")
    protocol: str = Field(..., description="协议: tcp/http/https")
    description: Optional[str] = Field("", description="描述")


class LBPoolCreateRequest(LBPoolBase):
    """创建后端池请求"""
    pass


class LBPoolUpdateRequest(BaseModel):
    """更新后端池请求"""
    name: Optional[str] = Field(None, max_length=100, description="名称")
    protocol: Optional[str] = Field(None, description="协议")
    description: Optional[str] = Field(None, description="描述")


class LBPoolResponse(LBPoolBase):
    """后端池响应"""
    id: int = Field(..., description="ID")
    loadbalancer_name: Optional[str] = Field(None, description="负载均衡器名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True