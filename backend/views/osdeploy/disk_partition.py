"""磁盘分区视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from backend.schemas.osdeploy.disk_partition import DiskPartitionRequest
from backend.services.osdeploy.disk_partition_service import DiskPartitionService
from backend.common import SuccessResponse, ErrorResponse, ErrCode


class DiskPartitionViewSet(viewsets.ViewSet):
    """磁盘分区管理视图集"""
    permission_classes = [IsAuthenticated]

    @action(['post'], False, url_path='info')
    def info(self, request):
        """获取远程主机磁盘信息"""
        host = request.data.get('host')
        username = request.data.get('username')
        password = request.data.get('password')
        port = int(request.data.get('port', '22'))

        if not all([host, username, password]):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host, username, password are required')

        result = DiskPartitionService.get_disk_info(host, port, username, password)
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=result['message'])
        return SuccessResponse(result['disks'], errmsg='获取磁盘信息成功')

    @action(['post'], False, url_path='partition')
    def partition(self, request):
        """执行磁盘分区"""
        try:
            req = DiskPartitionRequest.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        scheme = {'partitions': [p.model_dump() for p in (req.partitions or [])]}
        result = DiskPartitionService.execute_partition(
            req.disk, req.mode, scheme,
            req.host, int(req.port), req.username, req.password
        )
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=result['message'])
        return SuccessResponse(errmsg=result['message'])