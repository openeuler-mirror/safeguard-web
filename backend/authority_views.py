from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority
from backend.authority_serializers import (
    AuthoritySerializer, AuthorityCreateSerializer, AuthorityUpdateSerializer,
    MenuSerializer, MenuUpdateSerializer, MenuTreeSerializer, MenuButtonSerializer,
    UserAuthoritySerializer, SetUserRoleSerializer
)


class AuthorityViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    queryset = Authority.objects.all().order_by('authority_id')
    serializer_class = AuthoritySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AuthorityCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AuthorityUpdateSerializer
        return AuthoritySerializer

    @action(detail=True, methods=['get', 'put'], url_path='menus')
    def menus(self, request, pk=None):
        """获取/设置角色菜单"""
        authority = self.get_object()

        if request.method == 'GET':
            # 获取角色关联的菜单
            menus = Menu.objects.filter(authoritymenu__authority=authority)
            serializer = MenuSerializer(menus, many=True)
            return Response(serializer.data)

        elif request.method == 'PUT':
            menu_ids = request.data.get('menu_ids', [])
            # 先删除所有关联
            AuthorityMenu.objects.filter(authority=authority).delete()
            # 再创建新关联
            for menu_id in menu_ids:
                AuthorityMenu.objects.create(authority=authority, menu_id=menu_id)
            return Response({'message': '菜单绑定成功'})

    @action(detail=True, methods=['get', 'put'], url_path='btns')
    def btns(self, request, pk=None):
        """获取/设置角色按钮权限"""
        authority = self.get_object()

        if request.method == 'GET':
            # 获取角色关联的按钮
            button_relations = AuthorityButton.objects.filter(authority=authority).select_related('menu', 'button')
            buttons = [rel.button for rel in button_relations]
            serializer = MenuButtonSerializer(buttons, many=True)
            return Response(serializer.data)

        elif request.method == 'PUT':
            btn_data = request.data.get('buttons', [])  # [{menu_id, button_ids: []}]
            # 先删除所有按钮关联
            AuthorityButton.objects.filter(authority=authority).delete()
            # 再创建新关联
            for item in btn_data:
                menu_id = item.get('menu_id')
                button_ids = item.get('button_ids', [])
                for button_id in button_ids:
                    AuthorityButton.objects.create(
                        authority=authority,
                        menu_id=menu_id,
                        button_id=button_id
                    )
            return Response({'message': '按钮权限绑定成功'})

    @action(detail=True, methods=['post'], url_path='copy')
    def copy(self, request, pk=None):
        """复制角色"""
        authority = self.get_object()

        # 查找最大 authority_id
        max_id = Authority.objects.order_by('-authority_id').first()
        new_authority_id = (max_id.authority_id + 1) if max_id else 1

        # 创建新角色
        new_authority = Authority.objects.create(
            authority_id=new_authority_id,
            authority_name=f'{authority.authority_name}_副本',
            parent=authority.parent,
            default_router=authority.default_router,
            data_authority=authority.data_authority
        )

        # 复制菜单关联
        menu_ids = AuthorityMenu.objects.filter(authority=authority).values_list('menu_id', flat=True)
        for menu_id in menu_ids:
            AuthorityMenu.objects.create(authority=new_authority, menu_id=menu_id)

        # 复制按钮关联
        btn_relations = AuthorityButton.objects.filter(authority=authority)
        for rel in btn_relations:
            AuthorityButton.objects.create(
                authority=new_authority,
                menu=rel.menu,
                button=rel.button
            )

        return Response({
            'message': '角色复制成功',
            'id': new_authority.id
        }, status=status.HTTP_201_CREATED)


class MenuViewSet(viewsets.ModelViewSet):
    """菜单管理视图集"""
    queryset = Menu.objects.all().order_by('sort')
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return MenuUpdateSerializer
        return MenuSerializer

    @action(detail=False, methods=['get'], url_path='tree')
    def tree(self, request):
        """获取菜单树"""
        root_menus = Menu.objects.filter(parent__isnull=True).prefetch_related(
            Prefetch('children', queryset=Menu.objects.prefetch_related(
                Prefetch('children', queryset=Menu.objects.all())
            ))
        )
        serializer = MenuTreeSerializer(root_menus, many=True)
        return Response(serializer.data)
