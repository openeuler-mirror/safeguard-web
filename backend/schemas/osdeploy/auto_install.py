"""自动装机请求Schema"""
from pydantic import BaseModel, Field


class AutoInstallRequestSchema(BaseModel):
    """自动装机请求参数"""
    host_id: int = Field(..., description="目标主机ID")
    kickstart_id: int = Field(..., description="Kickstart模板ID")
    repo_id: int = Field(..., description="仓库ID")