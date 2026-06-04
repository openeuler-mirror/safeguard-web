"""Sensor 部署相关 Pydantic 模型"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class SensorDeploymentConfig(BaseModel):
    """Sensor 部署配置"""
    version: str = ""
    release: str = ""
    base_path: str = ""  # RPM 包基础路径
    arch: str = ""       # 目标架构 x86 / aarch64
    os_type: str = ""    # 系统版本 el7 / el9 / ule3
    host: str
    username: str
    password: str
    port: str = "22"


class SensorOperateRequest(BaseModel):
    """Sensor 操作请求"""
    host: str
    username: str
    password: str
    port: str = "22"
    operate: str  # start / stop / restart / delete


class SensorConfigUpdateRequest(BaseModel):
    """Sensor 配置更新请求"""
    config: Dict[str, Any]


class SensorInstallResponse(BaseModel):
    """Sensor 安装响应"""
    job_id: str
    status: str
    message: str
