"""RepoStatus Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class RepoStatusBase(BaseModel):
    """仓库状态基础模型"""
    name: str = Field(..., max_length=100, description="仓库名称")
    repo_type: str = Field(..., description="仓库类型: yum/iso/http")
    base_url: str = Field(..., description="仓库地址")
    is_default: bool = Field(False, description="是否默认仓库")
    description: str = Field("", description="描述")


class RepoStatusCreateRequest(RepoStatusBase):
    """创建仓库状态请求"""
    pass


class RepoStatusUpdateRequest(BaseModel):
    """更新仓库状态请求"""
    name: Optional[str] = Field(None, max_length=100, description="仓库名称")
    repo_type: Optional[str] = Field(None, description="仓库类型")
    base_url: Optional[str] = Field(None, description="仓库地址")
    is_default: Optional[bool] = Field(None, description="是否默认仓库")
    description: Optional[str] = Field(None, description="描述")


class RepoStatusResponse(RepoStatusBase):
    """仓库状态响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True