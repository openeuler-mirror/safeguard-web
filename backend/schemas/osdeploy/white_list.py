"""WhiteList Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class WhiteListBase(BaseModel):
    """MAC地址白名单基础模型"""
    mac_address: str = Field(..., max_length=17, description="MAC地址")
    hostname: str = Field("", max_length=255, description="主机名")
    ip_address: Optional[str] = Field(None, description="IP地址")
    description: str = Field("", description="描述")
    is_active: bool = Field(True, description="是否激活")


class WhiteListCreateRequest(WhiteListBase):
    """创建白名单请求"""
    pass


class WhiteListUpdateRequest(BaseModel):
    """更新白名单请求"""
    mac_address: Optional[str] = Field(None, max_length=17, description="MAC地址")
    hostname: Optional[str] = Field(None, max_length=255, description="主机名")
    ip_address: Optional[str] = Field(None, description="IP地址")
    description: Optional[str] = Field(None, description="描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class WhiteListResponse(WhiteListBase):
    """白名单响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True