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


class HostBase(BaseModel):
    """主机基础模型"""
    hostname: str = Field(..., max_length=255, description="主机名")
    ip_address: str = Field(..., description="管理IP")
    port: int = Field(22, description="SSH端口")
    username: str = Field(..., max_length=50, description="用户名")
    password: Optional[str] = Field("", max_length=255, description="密码")
    cluster: Optional[int] = Field(None, description="集群ID")
    status: str = Field("offline", description="状态: online/offline")
    os_type: Optional[str] = Field("", max_length=50, description="操作系统")


class HostCreateRequest(HostBase):
    """创建主机请求"""
    pass


class HostUpdateRequest(BaseModel):
    """更新主机请求"""
    hostname: Optional[str] = Field(None, max_length=255, description="主机名")
    port: Optional[int] = Field(None, description="SSH端口")
    username: Optional[str] = Field(None, max_length=50, description="用户名")
    password: Optional[str] = Field(None, max_length=255, description="密码")
    cluster: Optional[int] = Field(None, description="集群ID")
    status: Optional[str] = Field(None, description="状态")
    os_type: Optional[str] = Field(None, max_length=50, description="操作系统")


class HostResponse(HostBase):
    """主机响应"""
    id: int = Field(..., description="主机ID")
    cluster_name: Optional[str] = Field(None, description="集群名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True