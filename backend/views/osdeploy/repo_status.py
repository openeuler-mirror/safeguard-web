"""RepoStatus 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import RepoStatus
from backend.serializers.osdeploy import (
    RepoStatusSerializer,
    RepoStatusListSerializer,
    RepoStatusCreateSerializer,
    RepoStatusUpdateSerializer,
)
from backend.schemas.osdeploy import RepoStatusResponse
from backend.common import SuccessResponse, ErrorResponse, ErrCode
from backend.common.viewsets import UnifiedModelViewSet
from backend.services.osdeploy.repo_service import RepoService
from backend.services.task import TaskService
from backend.utils.ssh import SSHClient


class RepoViewSet(UnifiedModelViewSet):
    """仓库状态视图集"""
    queryset = RepoStatus.objects.all().order_by('id')
    serializer_class = RepoStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'repo_type', 'is_default']
    search_fields = ['name']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return RepoStatusCreateSerializer
        if self.action in ('update', 'partial_update'):
            return RepoStatusUpdateSerializer
        if self.action == 'list':
            return RepoStatusListSerializer
        return RepoStatusSerializer

    @extend_schema(
        summary="删除仓库",
        description="删除仓库前检查是否有关联的Kickstart模板",
        responses={
            200: OpenApiResponse(description="删除成功"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """删除仓库前检查是否有关联的 Kickstart"""
        repo = self.get_object()
        if repo.kickstartfilestatus_set.exists():
            return ErrorResponse(ErrCode.REPO_HAS_KICKSTART)
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="同步仓库",
        description="同步仓库内容",
        responses={200: OpenApiResponse(description="同步结果")}
    )
    @action(detail=True, methods=['post'], url_path='sync')
    def sync(self, request, pk=None):
        """同步仓库"""
        repo = self.get_object()
        result = RepoService.sync_repo(repo.id)
        return SuccessResponse(result)

    @extend_schema(
        summary="启用仓库",
        description="启用指定仓库",
        responses={200: OpenApiResponse(description="启用结果")}
    )
    @action(detail=True, methods=['post'], url_path='enable')
    def enable(self, request, pk=None):
        """启用仓库"""
        repo = self.get_object()
        result = RepoService.enable_repo(repo.id)
        return SuccessResponse(result)

    @extend_schema(
        summary="禁用仓库",
        description="禁用指定仓库",
        responses={200: OpenApiResponse(description="禁用结果")}
    )
    @action(detail=True, methods=['post'], url_path='disable')
    def disable(self, request, pk=None):
        """禁用仓库"""
        repo = self.get_object()
        result = RepoService.disable_repo(repo.id)
        return SuccessResponse(result)

    @extend_schema(
        summary="检查仓库",
        description="检查仓库可用性",
        responses={200: OpenApiResponse(description="检查结果")}
    )
    @action(detail=True, methods=['get'], url_path='check')
    def check(self, request, pk=None):
        """检查仓库"""
        repo = self.get_object()
        result = RepoService.check_repo(repo.id)
        return SuccessResponse(result)

    @action(detail=False, methods=['post'], url_path='create-iso')
    def create_iso(self, request):
        """从 ISO 创建远程仓库"""
        host = request.data.get('host')
        port = request.data.get('port', '22')
        username = request.data.get('username')
        password = request.data.get('password')
        iso_link = request.data.get('iso_link')

        if not all([host, username, password, iso_link]):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host, username, password, iso_link are required')

        job = TaskService.create_job(job_type='createrepoiso_remote', target=host, status='running')

        ssh = SSHClient(host=host, port=int(port), username=username, password=password, timeout=30)
        if not ssh.connect():
            TaskService.update_job(job.job_id, status='failed', error_message=f'无法连接到主机 {host}')
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=f'无法连接到主机 {host}')

        try:
            # 下载 ISO 并挂载创建仓库
            mount_dir = '/mnt/iso_repo'
            ssh.execute_command(f'mkdir -p {mount_dir}')
            stdout, stderr, exit_code = ssh.execute_command(f'wget -q -O /tmp/repo.iso {iso_link} && mount -o loop /tmp/repo.iso {mount_dir}')
            if exit_code != 0:
                TaskService.update_job(job.job_id, status='failed', error_message=f'ISO 下载或挂载失败: {stderr}')
                return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=f'ISO 下载或挂载失败: {stderr}')

            # 复制到本地 repo 目录
            repo_dir = '/var/www/html/repo'
            ssh.execute_command(f'mkdir -p {repo_dir} && cp -r {mount_dir}/* {repo_dir}/')
            ssh.execute_command(f'umount {mount_dir} && rm -f /tmp/repo.iso')

            TaskService.update_job(job.job_id, status='success', progress=100, result={'repo_dir': repo_dir})
            return SuccessResponse({'job_id': job.job_id, 'repo_dir': repo_dir}, errmsg='从 ISO 创建仓库成功')
        finally:
            ssh.close()

    @action(detail=True, methods=['post'], url_path='create-file')
    def create_file(self, request, pk=None):
        """在远程主机创建 repo 文件"""
        repo = self.get_object()
        if not getattr(repo, 'enabled', True):
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg='仓库未启用')

        host = request.data.get('host')
        port = request.data.get('port', '22')
        username = request.data.get('username')
        password = request.data.get('password')
        nobackup = request.data.get('nobackup', False)
        gpgcheck = request.data.get('gpgcheck', False)

        if not all([host, username, password]):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host, username, password are required')

        ssh = SSHClient(host=host, port=int(port), username=username, password=password, timeout=30)
        if not ssh.connect():
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=f'无法连接到主机 {host}')

        try:
            repo_file = f'/etc/yum.repos.d/{repo.name}.repo'
            if not nobackup:
                ssh.execute_command(f'cp {repo_file} {repo_file}.bak 2>/dev/null || true')

            content = f"""[{repo.name}]
name={repo.name}
baseurl={getattr(repo, 'base_url', '')}
gpgcheck={'1' if gpgcheck else '0'}
enabled=1
"""
            escaped = content.replace("'", "'\"'\"'")
            cmd = f"cat > {repo_file} << 'EOF_REPO'\n{escaped}\nEOF_REPO"
            stdout, stderr, exit_code = ssh.execute_command(cmd)
            if exit_code != 0:
                return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=f'创建 repo 文件失败: {stderr}')

            return SuccessResponse({'repo_file': repo_file}, errmsg='创建 repo 文件成功')
        finally:
            ssh.close()

    @extend_schema(
        summary="查询仓库任务状态",
        description="根据任务ID查询仓库相关任务的执行状态",
        responses={200: OpenApiResponse(description="任务状态")}
    )
    @action(detail=False, methods=['post'], url_path='query-job-status')
    def query_job_status(self, request):
        """查询仓库任务状态"""
        job_id = request.data.get('job_id')
        if not job_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='job_id is required')
        result = RepoService.query_repo_job_status(job_id)
        if result['success']:
            return SuccessResponse(result['job'], errmsg=result['message'])
        return ErrorResponse(ErrCode.NOT_FOUND, errmsg=result['message'])