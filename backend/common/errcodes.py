"""
错误码定义
错误码设计原则：
- 0: 成功
- 1xxx: 通用错误
- 2xxx: 认证/权限错误
- 3xxx: 用户相关错误
- 4xxx: 权限(Authority)相关错误
- 5xxx: 主机/集群相关错误
"""


class ErrCode:
    """错误码类，属性直接是错误码整数"""
    # 成功
    SUCCESS = 0

    # 通用错误 (1xxx)
    PARAM_ERROR = 1001
    PARAMETER_MISSING = 1002
    NOT_FOUND = 1004
    METHOD_NOT_ALLOWED = 1005
    OPERATION_FAILED = 1006
    INTERNAL_ERROR = 1500

    # 认证错误 (2xxx)
    AUTH_FAILED = 2001
    TOKEN_EXPIRED = 2002
    TOKEN_INVALID = 2003
    PERMISSION_DENIED = 2004

    # 用户相关 (3xxx)
    USER_NOT_FOUND = 3001
    USER_DISABLED = 3002
    USER_ALREADY_EXISTS = 3003
    PASSWORD_ERROR = 3004
    PASSWORD_TOO_SHORT = 3005
    EMAIL_ALREADY_EXISTS = 3006
    EMAIL_NOT_FOUND = 3007

    # 验证码相关 (31xx)
    VERIFY_CODE_ERROR = 3101
    VERIFY_CODE_EXPIRED = 3102
    VERIFY_CODE_USED = 3103
    VERIFY_CODE_NOT_FOUND = 3104
    CODE_SEND_FAILED = 3105

    # 权限相关 (4xxx)
    AUTHORITY_NOT_FOUND = 4001
    AUTHORITY_EXISTS = 4002
    USER_HAS_AUTHORITY = 4003
    USER_NOT_HAS_AUTHORITY = 4004
    MENU_NOT_FOUND = 4005
    MENU_HAS_CHILDREN = 4006

    # 主机相关 (5xxx)
    HOST_NOT_FOUND = 5001
    HOST_EXISTS = 5002
    CLUSTER_NOT_FOUND = 5003
    CLUSTER_HAS_HOSTS = 5004
    VM_NOT_FOUND = 5005
    VM_EXISTS = 5006
    HOST_HARDWARE_COLLECT_FAILED = 5007
    HOST_LLDP_COLLECT_FAILED = 5008
    HOST_PASSWORD_UPDATE_FAILED = 5009
    VM_OPERATION_FAILED = 5010

    # 用户-角色关联 (6xxx)
    USER_ROLE_SET_FAILED = 6001
    USER_ROLE_ADD_FAILED = 6002
    USER_ROLE_REMOVE_FAILED = 6003

    # OS部署相关 (7xxx)
    REPO_HAS_KICKSTART = 7001

    # Security/Safeguard相关 (72xx)
    DEPLOY_FAILED = 7201
    ROLLBACK_FAILED = 7202


# 错误码到描述的映射
_ERRCODE_MAP = {
    0: "操作成功",
    1001: "参数错误",
    1002: "缺少必要参数",
    1004: "资源不存在",
    1005: "请求方法不支持",
    1006: "操作失败",
    1500: "服务器内部错误",
    2001: "认证失败",
    2002: "token已过期",
    2003: "token无效",
    2004: "权限不足",
    3001: "用户不存在",
    3002: "用户已被禁用",
    3003: "用户已存在",
    3004: "密码错误",
    3005: "密码长度至少6位",
    3006: "邮箱已被注册",
    3007: "邮箱不存在",
    3101: "验证码错误",
    3102: "验证码已过期",
    3103: "验证码已被使用",
    3104: "验证码不存在",
    3105: "验证码发送失败",
    4001: "角色不存在",
    4002: "角色已存在",
    4003: "用户已有该角色",
    4004: "用户没有该角色",
    4005: "菜单不存在",
    4006: "菜单存在子菜单，无法删除",
    5001: "主机不存在",
    5002: "主机已存在",
    5003: "集群不存在",
    5004: "集群下存在主机，无法删除",
    5005: "虚拟机不存在",
    5006: "虚拟机已存在",
    5007: "主机硬件信息采集失败",
    5008: "主机LLDP信息采集失败",
    5009: "主机密码更新失败",
    5010: "虚拟机操作失败",
    6001: "角色设置失败",
    6002: "角色添加失败",
    6003: "角色移除失败",

    # OS部署相关 (7xxx)
    7001: "仓库存在关联的Kickstart模板，无法删除",

    # Security/Safeguard相关 (72xx)
    7201: "部署失败",
    7202: "回滚失败",
}


def get_errmsg(errno):
    """根据错误码获取错误描述"""
    return _ERRCODE_MAP.get(errno, "未知错误")
