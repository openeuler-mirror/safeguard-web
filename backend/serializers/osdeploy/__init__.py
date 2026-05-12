from backend.serializers.osdeploy.job_status import (
    JobStatusSerializer,
    JobStatusListSerializer,
)
from backend.serializers.osdeploy.repo_status import (
    RepoStatusSerializer,
    RepoStatusListSerializer,
    RepoStatusCreateSerializer,
    RepoStatusUpdateSerializer,
)
from backend.serializers.osdeploy.pxe_server_status import (
    PXEServerStatusSerializer,
    PXEServerStatusListSerializer,
    PXEServerStatusCreateSerializer,
    PXEServerStatusUpdateSerializer,
)
from backend.serializers.osdeploy.kickstart_file_status import (
    KickStartFileStatusSerializer,
    KickStartFileStatusListSerializer,
    KickStartFileStatusCreateSerializer,
    KickStartFileStatusUpdateSerializer,
)
from backend.serializers.osdeploy.iso_file_status import (
    ISOFileStatusSerializer,
    ISOFileStatusListSerializer,
    ISOFileStatusCreateSerializer,
    ISOFileStatusUpdateSerializer,
)
from backend.serializers.osdeploy.white_list import (
    WhiteListSerializer,
    WhiteListListSerializer,
    WhiteListCreateSerializer,
    WhiteListUpdateSerializer,
)
from backend.serializers.osdeploy.out_ip_sn import (
    OutIpSNSerializer,
    OutIpSNListSerializer,
    OutIpSNCreateSerializer,
    OutIpSNUpdateSerializer,
)

__all__ = [
    # JobStatus
    'JobStatusSerializer',
    'JobStatusListSerializer',
    # RepoStatus
    'RepoStatusSerializer',
    'RepoStatusListSerializer',
    'RepoStatusCreateSerializer',
    'RepoStatusUpdateSerializer',
    # PXEServerStatus
    'PXEServerStatusSerializer',
    'PXEServerStatusListSerializer',
    'PXEServerStatusCreateSerializer',
    'PXEServerStatusUpdateSerializer',
    # KickStartFileStatus
    'KickStartFileStatusSerializer',
    'KickStartFileStatusListSerializer',
    'KickStartFileStatusCreateSerializer',
    'KickStartFileStatusUpdateSerializer',
    # ISOFileStatus
    'ISOFileStatusSerializer',
    'ISOFileStatusListSerializer',
    'ISOFileStatusCreateSerializer',
    'ISOFileStatusUpdateSerializer',
    # WhiteList
    'WhiteListSerializer',
    'WhiteListListSerializer',
    'WhiteListCreateSerializer',
    'WhiteListUpdateSerializer',
    # OutIpSN
    'OutIpSNSerializer',
    'OutIpSNListSerializer',
    'OutIpSNCreateSerializer',
    'OutIpSNUpdateSerializer',
]