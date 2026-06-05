"""DHCP Relay Pydantic 模型"""
from pydantic import BaseModel


class DHCPRelayParams(BaseModel):
    """DHCP Relay 配置参数"""
    host: str
    username: str
    password: str
    port: str = "22"
    interface_name: str
    dhcp_relay_ip: str