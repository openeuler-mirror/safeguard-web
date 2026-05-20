"""LBMember Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class LBMemberBase(BaseModel):
    """池成员基础模型"""
    pool: int = Field(..., description="后端池ID")
    address: str = Field(..., description="成员地址")
    port: int = Field(..., description="端口")
    weight: int = Field(1, description="权重")
    is_enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field("", description="描述")


class LBMemberCreateRequest(LBMemberBase):
    """创建池成员请求"""
    pass


class LBMemberUpdateRequest(BaseModel):
    """更新池成员请求"""
    address: Optional[str] = Field(None, description="成员地址")
    port: Optional[int] = Field(None, description="端口")
    weight: Optional[int] = Field(None, description="权重")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class LBMemberResponse(LBMemberBase):
    """池成员响应"""
    id: int = Field(..., description="ID")
    pool_name: Optional[str] = Field(None, description="后端池名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True