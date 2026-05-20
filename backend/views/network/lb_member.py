"""LBMember 视图集"""
from rest_framework.permissions import IsAuthenticated

from backend.models.network import LBMember
from backend.serializers.network import (
    LBMemberSerializer,
    LBMemberListSerializer,
    LBMemberCreateSerializer,
    LBMemberUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet


class LBMemberViewSet(UnifiedModelViewSet):
    """池成员视图集"""
    queryset = LBMember.objects.select_related('pool').all().order_by('id')
    serializer_class = LBMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pool', 'is_enabled']
    search_fields = ['address']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return LBMemberCreateSerializer
        if self.action in ('update', 'partial_update'):
            return LBMemberUpdateSerializer
        if self.action == 'list':
            return LBMemberListSerializer
        return LBMemberSerializer