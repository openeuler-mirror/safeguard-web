"""API 协议定义 - Pydantic 模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础字段"""
    user: str = Field(..., min_length=1, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    uuid: str
    enable: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreateRequest(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, description="密码")


class UserUpdateRequest(BaseModel):
    """更新用户请求 (PUT me)"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码 (至少6位)")


class ResetPasswordRequest(BaseModel):
    """管理员重置密码请求"""
    new_password: str = Field(..., min_length=6, description="新密码 (至少6位)")


class SetRoleRequest(BaseModel):
    """设置用户角色请求"""
    role_id: int = Field(..., description="角色ID")


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """登录响应"""
    access: str = Field(..., description="JWT访问令牌")
    refresh: str = Field(..., description="JWT刷新令牌")