"""RPC 文件操作视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from backend.services.rpc.file_service import FileService
from backend.common import SuccessResponse, ErrorResponse


class FileViewSet(viewsets.ViewSet):
    """文件操作视图集"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='copy')
    def copy(self, request):
        """复制文件到远程主机"""
        srcfile = request.data.get('srcfile')
        destfile = request.data.get('destfile')
        host = request.data.get('host')
        port = int(request.data.get('port', 22))
        username = request.data.get('username')
        password = request.data.get('password')

        if not all([srcfile, destfile, host, username, password]):
            return ErrorResponse(400, errmsg='missing required parameters')

        success, message = FileService.file_copy(srcfile, destfile, host, port, username, password)
        if success:
            return SuccessResponse({'message': message})
        return ErrorResponse(500, errmsg=message)

    @action(detail=False, methods=['post'], url_path='download')
    def download(self, request):
        """从远程主机下载文件"""
        remote_path = request.data.get('remote_path')
        local_path = request.data.get('local_path')
        host = request.data.get('host')
        port = int(request.data.get('port', 22))
        username = request.data.get('username')
        password = request.data.get('password')

        if not all([remote_path, local_path, host, username, password]):
            return ErrorResponse(400, errmsg='missing required parameters')

        success, message = FileService.file_download(remote_path, local_path, host, port, username, password)
        if success:
            return SuccessResponse({'message': message})
        return ErrorResponse(500, errmsg=message)

    @action(detail=False, methods=['post'], url_path='exists')
    def exists(self, request):
        """检查远程文件是否存在"""
        remote_path = request.data.get('remote_path')
        host = request.data.get('host')
        port = int(request.data.get('port', 22))
        username = request.data.get('username')
        password = request.data.get('password')

        if not all([remote_path, host, username, password]):
            return ErrorResponse(400, errmsg='missing required parameters')

        exists, message = FileService.remote_file_exists(remote_path, host, port, username, password)
        return SuccessResponse({'exists': exists, 'message': message})
