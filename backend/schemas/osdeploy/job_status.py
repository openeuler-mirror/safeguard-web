"""JobStatus Pydantic 模型"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class JobStatusBase(BaseModel):
    """任务状态基础模型"""
    job_id: str = Field(..., max_length=100, description="任务ID")
    job_type: str = Field(..., description="任务类型: os_install/os_migrate/hardware_collect")
    target: str = Field(..., max_length=255, description="目标")
    status: str = Field("pending", description="状态: pending/running/success/failed")
    progress: int = Field(0, ge=0, le=100, description="进度百分比")
    result: Dict[str, Any] = Field(default_factory=dict, description="结果详情")
    error_message: str = Field("", description="错误信息")


class JobStatusCreateRequest(JobStatusBase):
    """创建任务状态请求"""
    pass


class JobStatusUpdateRequest(BaseModel):
    """更新任务状态请求"""
    status: Optional[str] = Field(None, description="状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="进度百分比")
    result: Optional[Dict[str, Any]] = Field(None, description="结果详情")
    error_message: Optional[str] = Field(None, description="错误信息")


class JobStatusResponse(JobStatusBase):
    """任务状态响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True