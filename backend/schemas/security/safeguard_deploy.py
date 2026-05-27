"""SafeguardDeploy Pydantic 模型"""
from typing import Optional, List
from pydantic import BaseModel, Field


class SafeguardDeployBase(BaseModel):
    """Safeguard部署基础模型"""
    name: str = Field(..., max_length=100, description="部署名称")
    target_hosts: List[str] = Field(default_factory=list, description="目标主机列表")
    safeguard_type: str = Field("safeguardx86", description="安全组件类型")
    arch: str = Field("x86", description="架构: x86/arm")
    host: str = Field("", description="目标主机IP")
    username: str = Field("", description="用户名")
    password: str = Field("", description="密码")
    port: str = Field("22", description="端口")
    description: Optional[str] = Field("", description="描述")


class SafeguardDeployCreateRequest(SafeguardDeployBase):
    """创建Safeguard部署请求"""
    pass


class SafeguardDeployUpdateRequest(BaseModel):
    """更新Safeguard部署请求"""
    name: Optional[str] = Field(None, max_length=100, description="部署名称")
    target_hosts: Optional[List[str]] = Field(None, description="目标主机列表")
    safeguard_type: Optional[str] = Field(None, description="安全组件类型")
    arch: Optional[str] = Field(None, description="架构")
    host: Optional[str] = Field(None, description="目标主机IP")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    port: Optional[str] = Field(None, description="端口")
    status: Optional[str] = Field(None, description="状态")
    description: Optional[str] = Field(None, description="描述")


class SafeguardDeployResponse(SafeguardDeployBase):
    """Safeguard部署响应"""
    id: int = Field(..., description="ID")
    status: str = Field(..., description="状态")
    result: dict = Field(default_factory=dict, description="结果详情")
    error_message: str = Field("", description="错误信息")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True