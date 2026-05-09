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


class VMBase(BaseModel):
    """VM基础模型"""
    name: str = Field(..., max_length=255, description="VM名称")
    uuid: str = Field(..., max_length=100, description="UUID")
    host: int = Field(..., description="宿主机ID")
    cluster: Optional[int] = Field(None, description="集群ID")
    status: str = Field("stopped", description="状态: stopped/running/paused/suspended")
    vcpu: int = Field(1, description="虚拟CPU核数")
    memory: int = Field(0, description="内存(字节)")
    disk: int = Field(0, description="磁盘(字节)")
    ip_address: Optional[str] = Field(None, description="IP地址")
    mac_address: Optional[str] = Field("", max_length=17, description="MAC地址")
    os_type: Optional[str] = Field("", max_length=50, description="操作系统")


class VMCreateRequest(VMBase):
    """创建VM请求"""
    pass


class VMUpdateRequest(BaseModel):
    """更新VM请求"""
    name: Optional[str] = Field(None, max_length=255, description="VM名称")
    host: Optional[int] = Field(None, description="宿主机ID")
    cluster: Optional[int] = Field(None, description="集群ID")
    status: Optional[str] = Field(None, description="状态")
    vcpu: Optional[int] = Field(None, description="虚拟CPU核数")
    memory: Optional[int] = Field(None, description="内存(字节)")
    disk: Optional[int] = Field(None, description="磁盘(字节)")
    ip_address: Optional[str] = Field(None, description="IP地址")
    mac_address: Optional[str] = Field(None, max_length=17, description="MAC地址")
    os_type: Optional[str] = Field(None, max_length=50, description="操作系统")


class VMResponse(VMBase):
    """VM响应"""
    id: int = Field(..., description="VM ID")
    host_name: Optional[str] = Field(None, description="宿主机名称")
    cluster_name: Optional[str] = Field(None, description="集群名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True