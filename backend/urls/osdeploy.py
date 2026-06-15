"""OS部署相关 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.osdeploy import (
    JobViewSet,
    RepoViewSet,
    PXEServerStatusViewSet,
    KickStartViewSet,
    AutoInstallViewSet,
    SensorViewSet,
    NoVNCViewSet,
    DiskPartitionViewSet,
    PackageViewSet,
    ISOFileStatusViewSet,
    OutIpSNViewSet,
    WhiteListViewSet,
)

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'repos', RepoViewSet, basename='repo')
router.register(r'pxe-servers', PXEServerStatusViewSet, basename='pxe-server')
router.register(r'kickstarts', KickStartViewSet, basename='kickstart')
router.register(r'autoinstall', AutoInstallViewSet, basename='autoinstall')
router.register(r'sensors', SensorViewSet, basename='sensor')
router.register(r'novnc', NoVNCViewSet, basename='novnc')
router.register(r'disk-partition', DiskPartitionViewSet, basename='disk-partition')
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'isos', ISOFileStatusViewSet, basename='iso')
router.register(r'outipsn', OutIpSNViewSet, basename='outipsn')
router.register(r'whitelist', WhiteListViewSet, basename='whitelist')

urlpatterns = [
    path('', include(router.urls)),
]