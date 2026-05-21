"""KickStartFileStatus Pydantic 模型"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class KickStartFileStatusBase(BaseModel):
    """Kickstart文件状态基础模型"""
    name: str = Field(..., max_length=100, description="模板名称")
    content: str = Field(..., description="模板内容")
    repo: Optional[int] = Field(None, description="关联仓库ID")
    kernel_options: Dict[str, Any] = Field(default_factory=dict, description="内核参数")
    description: str = Field("", description="描述")


class KickStartFileStatusCreateRequest(KickStartFileStatusBase):
    """创建Kickstart文件状态请求"""
    pass


class KickStartFileStatusUpdateRequest(BaseModel):
    """更新Kickstart文件状态请求"""
    name: Optional[str] = Field(None, max_length=100, description="模板名称")
    content: Optional[str] = Field(None, description="模板内容")
    repo: Optional[int] = Field(None, description="关联仓库ID")
    kernel_options: Optional[Dict[str, Any]] = Field(None, description="内核参数")
    description: Optional[str] = Field(None, description="描述")


class KickStartFileStatusResponse(KickStartFileStatusBase):
    """Kickstart文件状态响应"""
    id: int = Field(..., description="ID")
    repo_name: Optional[str] = Field(None, description="关联仓库名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True