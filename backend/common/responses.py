"""
统一响应结构
响应格式：{errno: int, errmsg: str, data: any}
"""
from rest_framework.response import Response
from backend.common.errcodes import ErrCode, get_errmsg


class ApiResponse(Response):
    """
    统一 API 响应格式
    响应结构：{errno: int, errmsg: str, data: any}
    """

    def __init__(self, errno=0, data=None, errmsg=None, status=None):
        """
        Args:
            errno: 错误码，0表示成功
            data: 响应数据，errno不为0时通常为空
            errmsg: 错误信息，如果为None则自动从错误码获取
            status: HTTP状态码，默认200
        """
        if errmsg is None:
            errmsg = get_errmsg(errno)

        super().__init__(
            data={
                'errno': errno,
                'errmsg': errmsg,
                'data': data if errno == 0 else None
            },
            status=status if status is not None else 200
        )


class SuccessResponse(ApiResponse):
    """成功响应"""

    def __init__(self, data=None, errmsg=None):
        super().__init__(errno=0, data=data, errmsg=errmsg)


class ErrorResponse(ApiResponse):
    """错误响应"""

    def __init__(self, errno, data=None, errmsg=None):
        if errmsg is None:
            errmsg = get_errmsg(errno)
        super().__init__(errno=errno, data=data, errmsg=errmsg)
