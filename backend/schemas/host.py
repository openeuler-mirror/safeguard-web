"""主机相关 Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class ClusterBase(BaseModel):
    """集群基础模型"""
    name: str = Field(..., max_length=100, description="集群名称")
    description: Optional[str] = Field("", description="描述")
    vcenter_id: Optional[str] = Field("", max_length=100, description="vCenter ID")


class ClusterCreateRequest(ClusterBase):
    """创建集群请求"""
    pass


class ClusterUpdateRequest(ClusterBase):
    """更新集群请求"""
    pass


class ClusterResponse(ClusterBase):
    """集群响应"""
    id: int = Field(..., description="集群ID")
    host_count: int = Field(0, description="关联主机数量")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True