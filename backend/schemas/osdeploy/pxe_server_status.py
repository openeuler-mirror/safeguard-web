"""PXEServerStatus Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class PXEServerStatusBase(BaseModel):
    """PXE服务器状态基础模型"""
    server_ip: str = Field(..., description="服务器IP")
    interface: str = Field("eth0", max_length=100, description="网卡")
    dhcp_range_start: str = Field(..., description="DHCP起始IP")
    dhcp_range_end: str = Field(..., description="DHCP结束IP")
    status: str = Field("active", description="状态: active/inactive")
    description: Optional[str] = Field("", description="描述")


class PXEServerStatusCreateRequest(PXEServerStatusBase):
    """创建PXE服务器状态请求"""
    pass


class PXEServerStatusUpdateRequest(BaseModel):
    """更新PXE服务器状态请求"""
    server_ip: Optional[str] = Field(None, description="服务器IP")
    interface: Optional[str] = Field(None, max_length=100, description="网卡")
    dhcp_range_start: Optional[str] = Field(None, description="DHCP起始IP")
    dhcp_range_end: Optional[str] = Field(None, description="DHCP结束IP")
    status: Optional[str] = Field(None, description="状态")
    description: Optional[str] = Field(None, description="描述")


class PXEServerStatusResponse(PXEServerStatusBase):
    """PXE服务器状态响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True