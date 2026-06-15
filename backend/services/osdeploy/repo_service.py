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
        """同步仓库

        区分 repo_type（yum/iso/http）执行不同的同步逻辑：
        - yum/http：尝试 urlopen 探测可用性，并尝试执行 reposync/createrepo（本地环境不存在命令时不报错）
        - iso：检查挂载路径/ISO 文件是否存在

        同时创建 Task 记录（job_type='repo_sync'）并返回结果。
        """
        import os
        import shutil
        import subprocess
        import urllib.request
        import urllib.error
        import uuid

        from backend.models.task import Task

        try:
            repo = RepoStatus.objects.get(pk=repo_id)
        except RepoStatus.DoesNotExist:
            raise ValueError(f"仓库不存在: {repo_id}")

        job_id = f"repo_sync_{repo_id}_{uuid.uuid4().hex[:8]}"
        task = Task.objects.create(
            job_id=job_id,
            job_type="repo_sync",
            target=repo.name,
            status="running",
            progress=0,
            result={},
        )

        errors = []
        warnings = []
        synced = False

        repo_type = repo.repo_type
        base_url = repo.base_url or ""

        try:
            if repo_type in ("yum", "http"):
                # 1) 网络可用性探测
                try:
                    req = urllib.request.Request(base_url, method="HEAD")
                    urllib.request.urlopen(req, timeout=10)
                    warnings.append("仓库 URL 可访问")
                except urllib.error.URLError as e:
                    errors.append(f"仓库 URL 不可访问: {e}")
                except urllib.error.HTTPError as e:
                    errors.append(f"仓库 URL 返回 HTTP 错误: {e.code}")
                except Exception as e:
                    warnings.append(f"URL 探测异常（非致命）: {e}")

                # 2) 尝试 reposync（本地不存在命令时不报错）
                if shutil.which("reposync"):
                    try:
                        subprocess.run(
                            ["reposync", "-n", "--repoid", repo.name, "-p", "/tmp/reposync"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        warnings.append("reposync 预检成功")
                    except subprocess.CalledProcessError as e:
                        warnings.append(f"reposync 预检失败: {e.stderr}")
                else:
                    warnings.append("reposync 命令未安装，跳过")

                # 3) 尝试 createrepo（本地不存在命令时不报错）
                if shutil.which("createrepo") or shutil.which("createrepo_c"):
                    try:
                        cmd = "createrepo_c" if shutil.which("createrepo_c") else "createrepo"
                        subprocess.run(
                            [cmd, "/tmp/reposync/" + repo.name],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        warnings.append("createrepo 成功")
                    except subprocess.CalledProcessError as e:
                        warnings.append(f"createrepo 失败: {e.stderr}")
                else:
                    warnings.append("createrepo 命令未安装，跳过")

                synced = len(errors) == 0

            elif repo_type == "iso":
                # ISO 类型：检查挂载路径或 ISO 文件
                iso_path = base_url
                if iso_path.startswith("file://"):
                    iso_path = iso_path[len("file://"):]

                if os.path.isfile(iso_path):
                    warnings.append(f"ISO 文件存在: {iso_path}")
                elif os.path.isdir(iso_path):
                    warnings.append(f"ISO 挂载目录存在: {iso_path}")
                else:
                    errors.append(f"ISO 文件或挂载路径不存在: {iso_path}")

                synced = len(errors) == 0

            else:
                errors.append(f"不支持的仓库类型: {repo_type}")

            # 更新 Task 状态
            task.status = "success" if synced else "failed"
            task.progress = 100 if synced else 50
            task.result = {
                "repo_id": repo_id,
                "repo_name": repo.name,
                "repo_type": repo_type,
                "synced": synced,
                "warnings": warnings,
            }
            task.error_message = "; ".join(errors) if errors else ""
            task.save()

            return {
                "repo_id": repo_id,
                "repo_name": repo.name,
                "repo_type": repo_type,
                "status": "synced" if synced else "failed",
                "job_id": job_id,
                "message": "仓库同步完成" if synced else "仓库同步失败",
                "warnings": warnings,
                "errors": errors,
            }

        except Exception as e:
            task.status = "failed"
            task.progress = 0
            task.error_message = str(e)
            task.save()
            raise

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
