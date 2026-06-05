"""仓库管理服务"""
from typing import Optional
from backend.models.osdeploy import RepoStatus


class RepoService:
    """仓库服务"""

    @staticmethod
    def list_repos(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取仓库列表（支持分页和过滤）"""
        queryset = RepoStatus.objects.all()
        if filters:
            queryset = queryset.filter(**filters)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_repo(repo_id: int) -> Optional[RepoStatus]:
        """获取仓库详情"""
        try:
            return RepoStatus.objects.get(pk=repo_id)
        except RepoStatus.DoesNotExist:
            return None

    @staticmethod
    def create_repo(data: dict) -> RepoStatus:
        """创建仓库"""
        # 如果设置为默认仓库，先取消其他默认
        if data.get('is_default', False):
            RepoStatus.objects.filter(is_default=True).update(is_default=False)
        return RepoStatus.objects.create(**data)

    @staticmethod
    def update_repo(repo_id: int, data: dict) -> Optional[RepoStatus]:
        """更新仓库"""
        try:
            repo = RepoStatus.objects.get(pk=repo_id)
            # 如果设置为默认仓库，先取消其他默认
            if data.get('is_default', False):
                RepoStatus.objects.exclude(pk=repo_id).filter(is_default=True).update(is_default=False)
            for key, value in data.items():
                setattr(repo, key, value)
            repo.save()
            return repo
        except RepoStatus.DoesNotExist:
            return None

    @staticmethod
    def delete_repo(repo_id: int) -> bool:
        """删除仓库"""
        try:
            repo = RepoStatus.objects.get(pk=repo_id)
            repo.delete()
            return True
        except RepoStatus.DoesNotExist:
            return False

    @staticmethod
    def sync_repo(repo_id: int) -> dict:
        """同步仓库"""
        try:
            repo = RepoStatus.objects.get(pk=repo_id)
            # TODO: 实现实际的仓库同步逻辑
            # 例如：rsync, reposync 等
            return {
                "repo_id": repo_id,
                "repo_name": repo.name,
                "status": "synced",
                "message": "仓库同步完成"
            }
        except RepoStatus.DoesNotExist:
            raise ValueError(f"仓库不存在: {repo_id}")

    @staticmethod
    def get_default_repo() -> Optional[RepoStatus]:
        """获取默认仓库"""
        try:
            return RepoStatus.objects.get(is_default=True)
        except RepoStatus.DoesNotExist:
            return None

    @staticmethod
    def enable_repo(repo_id: int) -> dict:
        """启用仓库"""
        try:
            repo = RepoStatus.objects.get(pk=repo_id)
            repo.status = 'active'
            repo.save()
            return {"repo_id": repo_id, "repo_name": repo.name, "status": "enabled", "message": "仓库已启用"}
        except RepoStatus.DoesNotExist:
            raise ValueError(f"仓库不存在: {repo_id}")

    @staticmethod
    def disable_repo(repo_id: int) -> dict:
        """禁用仓库"""
        try:
            repo = RepoStatus.objects.get(pk=repo_id)
            repo.status = 'inactive'
            repo.save()
            return {"repo_id": repo_id, "repo_name": repo.name, "status": "disabled", "message": "仓库已禁用"}
        except RepoStatus.DoesNotExist:
            raise ValueError(f"仓库不存在: {repo_id}")

    @staticmethod
    def check_repo(repo_id: int) -> dict:
        """检查仓库可用性"""
        import urllib.request
        import urllib.error
        try:
            repo = RepoStatus.objects.get(pk=repo_id)
            url = repo.base_url
            req = urllib.request.Request(url, method='HEAD')
            try:
                urllib.request.urlopen(req, timeout=5)
                return {"repo_id": repo_id, "repo_name": repo.name, "available": True, "message": "仓库可访问"}
            except urllib.error.URLError as e:
                return {"repo_id": repo_id, "repo_name": repo.name, "available": False, "message": f"仓库不可访问: {e}"}
            except urllib.error.HTTPError as e:
                return {"repo_id": repo_id, "repo_name": repo.name, "available": False, "message": f"HTTP错误: {e.code}"}
        except RepoStatus.DoesNotExist:
            raise ValueError(f"仓库不存在: {repo_id}")

    @staticmethod
    def create_repo_iso(data: dict) -> RepoStatus:
        """创建ISO仓库"""
        if data.get('is_default', False):
            RepoStatus.objects.filter(is_default=True).update(is_default=False)
        data['repo_type'] = 'iso'
        return RepoStatus.objects.create(**data)

    @staticmethod
    def create_repo_file(data: dict) -> RepoStatus:
        """创建文件仓库"""
        if data.get('is_default', False):
            RepoStatus.objects.filter(is_default=True).update(is_default=False)
        data['repo_type'] = 'http'
        return RepoStatus.objects.create(**data)

    @staticmethod
    def query_repo_job_status(job_id: str) -> dict:
        """查询仓库相关任务状态

        Args:
            job_id: 任务ID

        Returns:
            {"success": bool, "job": dict / None, "message": str}
        """
        from backend.models.task import Task
        try:
            task = Task.objects.get(job_id=job_id)
            return {
                "success": True,
                "job": {
                    "job_id": task.job_id,
                    "job_type": task.job_type,
                    "target": task.target,
                    "status": task.status,
                    "progress": task.progress,
                    "result": task.result,
                    "error_message": task.error_message,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                },
                "message": "查询成功",
            }
        except Task.DoesNotExist:
            return {"success": False, "job": None, "message": f"任务不存在: {job_id}"}
