"""LBHealthMonitor Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class LBHealthMonitorBase(BaseModel):
    """健康检查基础模型"""
    pool: int = Field(..., description="后端池ID")
    monitor_type: str = Field(..., description="检查类型: tcp/http/ping")
    interval: int = Field(5, description="检查间隔(秒)")
    timeout: int = Field(3, description="超时(秒)")
    retry: int = Field(3, description="重试次数")
    description: Optional[str] = Field("", description="描述")


class LBHealthMonitorCreateRequest(LBHealthMonitorBase):
    """创建健康检查请求"""
    pass


class LBHealthMonitorUpdateRequest(BaseModel):
    """更新健康检查请求"""
    monitor_type: Optional[str] = Field(None, description="检查类型")
    interval: Optional[int] = Field(None, description="检查间隔(秒)")
    timeout: Optional[int] = Field(None, description="超时(秒)")
    retry: Optional[int] = Field(None, description="重试次数")
    description: Optional[str] = Field(None, description="描述")


class LBHealthMonitorResponse(LBHealthMonitorBase):
    """健康检查响应"""
    id: int = Field(..., description="ID")
    pool_name: Optional[str] = Field(None, description="后端池名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True