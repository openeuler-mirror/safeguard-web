"""LoadBalancer Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class LoadBalancerBase(BaseModel):
    """负载均衡器基础模型"""
    name: str = Field(..., max_length=100, description="名称")
    vip_address: str = Field(..., description="VIP地址")
    port: int = Field(80, description="端口")
    algorithm: str = Field("round_robin", description="负载算法: round_robin/least_conn/source")
    status: str = Field("active", description="状态: active/inactive")
    description: Optional[str] = Field("", description="描述")


class LoadBalancerCreateRequest(LoadBalancerBase):
    """创建负载均衡器请求"""
    pass


class LoadBalancerUpdateRequest(BaseModel):
    """更新负载均衡器请求"""
    name: Optional[str] = Field(None, max_length=100, description="名称")
    vip_address: Optional[str] = Field(None, description="VIP地址")
    port: Optional[int] = Field(None, description="端口")
    algorithm: Optional[str] = Field(None, description="负载算法")
    status: Optional[str] = Field(None, description="状态")
    description: Optional[str] = Field(None, description="描述")


class LoadBalancerResponse(LoadBalancerBase):
    """负载均衡器响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True