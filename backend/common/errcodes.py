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
    # 成功
    SUCCESS = (0, "操作成功")

    # 通用错误 (1xxx)
    PARAM_ERROR = (1001, "参数错误")
    NOT_FOUND = (1004, "资源不存在")
    METHOD_NOT_ALLOWED = (1005, "请求方法不支持")
    INTERNAL_ERROR = (1500, "服务器内部错误")

    # 认证错误 (2xxx)
    AUTH_FAILED = (2001, "认证失败")
    TOKEN_EXPIRED = (2002, "token已过期")
    TOKEN_INVALID = (2003, "token无效")
    PERMISSION_DENIED = (2004, "权限不足")

    # 用户相关 (3xxx)
    USER_NOT_FOUND = (3001, "用户不存在")
    USER_DISABLED = (3002, "用户已被禁用")
    USER_ALREADY_EXISTS = (3003, "用户已存在")
    PASSWORD_ERROR = (3004, "密码错误")
    PASSWORD_TOO_SHORT = (3005, "密码长度至少6位")
    EMAIL_ALREADY_EXISTS = (3006, "邮箱已被注册")
    EMAIL_NOT_FOUND = (3007, "邮箱不存在")

    # 验证码相关 (31xx)
    VERIFY_CODE_ERROR = (3101, "验证码错误")
    VERIFY_CODE_EXPIRED = (3102, "验证码已过期")
    VERIFY_CODE_USED = (3103, "验证码已被使用")
    VERIFY_CODE_NOT_FOUND = (3104, "验证码不存在")
    CODE_SEND_FAILED = (3105, "验证码发送失败")

    # 权限相关 (4xxx)
    AUTHORITY_NOT_FOUND = (4001, "角色不存在")
    AUTHORITY_EXISTS = (4002, "角色已存在")
    USER_HAS_AUTHORITY = (4003, "用户已有该角色")
    USER_NOT_HAS_AUTHORITY = (4004, "用户没有该角色")
    MENU_NOT_FOUND = (4005, "菜单不存在")
    MENU_HAS_CHILDREN = (4006, "菜单存在子菜单，无法删除")

    # 主机相关 (5xxx)
    HOST_NOT_FOUND = (5001, "主机不存在")
    HOST_EXISTS = (5002, "主机已存在")
    CLUSTER_NOT_FOUND = (5003, "集群不存在")
    CLUSTER_HAS_HOSTS = (5004, "集群下存在主机，无法删除")
    VM_NOT_FOUND = (5005, "虚拟机不存在")
    VM_EXISTS = (5006, "虚拟机已存在")

    # 用户-角色关联 (6xxx)
    USER_ROLE_SET_FAILED = (6001, "角色设置失败")
    USER_ROLE_ADD_FAILED = (6002, "角色添加失败")
    USER_ROLE_REMOVE_FAILED = (6003, "角色移除失败")


# 动态生成错误码到描述的映射
def _build_errcode_map():
    """从 ErrCode 类属性中动态提取错误码和描述"""
    _map = {}
    for name in dir(ErrCode):
        if name.startswith('_'):
            continue
        value = getattr(ErrCode, name)
        if isinstance(value, tuple) and len(value) == 2:
            errno, errmsg = value
            if isinstance(errno, int):
                _map[errno] = errmsg
    return _map


_ERRCODE_MAP = _build_errcode_map()


def get_errmsg(errno):
    """根据错误码获取错误描述"""
    return _ERRCODE_MAP.get(errno, "未知错误")
