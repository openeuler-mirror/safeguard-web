"""ISOFileStatus Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class ISOFileStatusBase(BaseModel):
    """ISO文件状态基础模型"""
    filename: str = Field(..., max_length=255, description="文件名")
    size: int = Field(..., description="文件大小(字节)")
    md5sum: str = Field(..., max_length=32, description="MD5校验")
    status: str = Field("available", description="状态: available/uploading/error")


class ISOFileStatusCreateRequest(ISOFileStatusBase):
    """创建ISO文件状态请求"""
    pass


class ISOFileStatusUpdateRequest(BaseModel):
    """更新ISO文件状态请求"""
    status: Optional[str] = Field(None, description="状态")


class ISOFileStatusResponse(ISOFileStatusBase):
    """ISO文件状态响应"""
    id: int = Field(..., description="ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True