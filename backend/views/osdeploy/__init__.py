"""OS部署视图集"""
from backend.views.osdeploy.job_status import JobViewSet
from backend.views.osdeploy.repo_status import RepoViewSet
from backend.views.osdeploy.pxe_server_status import PXEServerStatusViewSet
from backend.views.osdeploy.kickstart_file_status import KickStartViewSet

__all__ = [
    'JobViewSet',
    'RepoViewSet',
    'PXEServerStatusViewSet',
    'KickStartViewSet',
]