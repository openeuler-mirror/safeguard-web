"""OS部署视图集"""
from backend.views.osdeploy.job_status import JobViewSet
from backend.views.osdeploy.repo_status import RepoViewSet
from backend.views.osdeploy.pxe_server_status import PXEServerStatusViewSet
from backend.views.osdeploy.kickstart_file_status import KickStartViewSet
from backend.views.osdeploy.auto_install import AutoInstallViewSet
from backend.views.osdeploy.sensor import SensorViewSet
from backend.views.osdeploy.novnc import NoVNCViewSet
from backend.views.osdeploy.disk_partition import DiskPartitionViewSet
from backend.views.osdeploy.package import PackageViewSet
from backend.views.osdeploy.iso_file_status import ISOFileStatusViewSet
from backend.views.osdeploy.out_ip_sn import OutIpSNViewSet
from backend.views.osdeploy.white_list import WhiteListViewSet

__all__ = [
    'JobViewSet',
    'RepoViewSet',
    'PXEServerStatusViewSet',
    'KickStartViewSet',
    'AutoInstallViewSet',
    'SensorViewSet',
    'NoVNCViewSet',
    'DiskPartitionViewSet',
    'PackageViewSet',
    'ISOFileStatusViewSet',
    'OutIpSNViewSet',
    'WhiteListViewSet',
]