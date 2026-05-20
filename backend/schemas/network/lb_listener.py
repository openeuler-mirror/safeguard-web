"""LBListener Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class LBListenerBase(BaseModel):
    """监听器基础模型"""
    loadbalancer: int = Field(..., description="负载均衡器ID")
    protocol: str = Field(..., description="协议: tcp/http/https")
    port: int = Field(..., description="端口")
    name: Optional[str] = Field("", max_length=100, description="名称")
    description: Optional[str] = Field("", description="描述")


class LBListenerCreateRequest(LBListenerBase):
    """创建监听器请求"""
    pass


class LBListenerUpdateRequest(BaseModel):
    """更新监听器请求"""
    protocol: Optional[str] = Field(None, description="协议")
    port: Optional[int] = Field(None, description="端口")
    name: Optional[str] = Field(None, max_length=100, description="名称")
    description: Optional[str] = Field(None, description="描述")


class LBListenerResponse(LBListenerBase):
    """监听器响应"""
    id: int = Field(..., description="ID")
    loadbalancer_name: Optional[str] = Field(None, description="负载均衡器名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True