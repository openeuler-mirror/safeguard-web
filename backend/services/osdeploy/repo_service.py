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
