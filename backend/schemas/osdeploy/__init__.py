"""OSDeploy 模块 Pydantic 模型"""
from backend.schemas.osdeploy.job_status import (
    JobStatusBase,
    JobStatusCreateRequest,
    JobStatusUpdateRequest,
    JobStatusResponse,
)
from backend.schemas.osdeploy.repo_status import (
    RepoStatusBase,
    RepoStatusCreateRequest,
    RepoStatusUpdateRequest,
    RepoStatusResponse,
)
from backend.schemas.osdeploy.pxe_server_status import (
    PXEServerStatusBase,
    PXEServerStatusCreateRequest,
    PXEServerStatusUpdateRequest,
    PXEServerStatusResponse,
)
from backend.schemas.osdeploy.kickstart_file_status import (
    KickStartFileStatusBase,
    KickStartFileStatusCreateRequest,
    KickStartFileStatusUpdateRequest,
    KickStartFileStatusResponse,
)
from backend.schemas.osdeploy.iso_file_status import (
    ISOFileStatusBase,
    ISOFileStatusCreateRequest,
    ISOFileStatusUpdateRequest,
    ISOFileStatusResponse,
)
from backend.schemas.osdeploy.white_list import (
    WhiteListBase,
    WhiteListCreateRequest,
    WhiteListUpdateRequest,
    WhiteListResponse,
)
from backend.schemas.osdeploy.out_ip_sn import (
    OutIpSNBase,
    OutIpSNCreateRequest,
    OutIpSNUpdateRequest,
    OutIpSNResponse,
)

__all__ = [
    'JobStatusBase',
    'JobStatusCreateRequest',
    'JobStatusUpdateRequest',
    'JobStatusResponse',
    'RepoStatusBase',
    'RepoStatusCreateRequest',
    'RepoStatusUpdateRequest',
    'RepoStatusResponse',
    'PXEServerStatusBase',
    'PXEServerStatusCreateRequest',
    'PXEServerStatusUpdateRequest',
    'PXEServerStatusResponse',
    'KickStartFileStatusBase',
    'KickStartFileStatusCreateRequest',
    'KickStartFileStatusUpdateRequest',
    'KickStartFileStatusResponse',
    'ISOFileStatusBase',
    'ISOFileStatusCreateRequest',
    'ISOFileStatusUpdateRequest',
    'ISOFileStatusResponse',
    'WhiteListBase',
    'WhiteListCreateRequest',
    'WhiteListUpdateRequest',
    'WhiteListResponse',
    'OutIpSNBase',
    'OutIpSNCreateRequest',
    'OutIpSNUpdateRequest',
    'OutIpSNResponse',
]