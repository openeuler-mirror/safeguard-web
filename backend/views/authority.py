from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Prefetch

from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton
from backend.serializers.authority import (
    AuthoritySerializer, AuthorityCreateSerializer, AuthorityUpdateSerializer,
    MenuSerializer, MenuUpdateSerializer, MenuTreeSerializer, MenuButtonSerializer,
)
from backend.permissions import AuthorityPermission
from backend.common import ErrCode, SuccessResponse, ErrorResponse, UnifiedModelViewSet


class AuthorityViewSet(UnifiedModelViewSet):
    """角色管理视图集"""
    queryset = Authority.objects.all().order_by('authority_id')
    serializer_class = AuthoritySerializer
    permission_classes = [AuthorityPermission]

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
            menus = Menu.objects.filter(authoritymenu__authority=authority)
            serializer = MenuSerializer(menus, many=True)
            return SuccessResponse(serializer.data)

        elif request.method == 'PUT':
            menu_ids = request.data.get('menu_ids', [])
            unique_menu_ids = set(menu_ids)
            if Menu.objects.filter(id__in=unique_menu_ids).count() != len(unique_menu_ids):
                return ErrorResponse(ErrCode.MENU_NOT_FOUND)

            with transaction.atomic():
                AuthorityMenu.objects.filter(authority=authority).delete()
                for menu_id in unique_menu_ids:
                    AuthorityMenu.objects.create(authority=authority, menu_id=menu_id)
            return SuccessResponse(errmsg='菜单绑定成功')

    @action(detail=True, methods=['get', 'put'], url_path='btns')
    def btns(self, request, pk=None):
        """获取/设置角色按钮权限"""
        authority = self.get_object()

        if request.method == 'GET':
            button_relations = AuthorityButton.objects.filter(authority=authority).select_related('menu', 'button')
            buttons = [rel.button for rel in button_relations]
            serializer = MenuButtonSerializer(buttons, many=True)
            return SuccessResponse(serializer.data)

        elif request.method == 'PUT':
            btn_data = request.data.get('buttons', [])
            menu_ids = [item.get('menu_id') for item in btn_data]
            button_ids = [
                button_id
                for item in btn_data
                for button_id in item.get('button_ids', [])
            ]
            unique_menu_ids = set(menu_ids)
            unique_button_ids = set(button_ids)
            if Menu.objects.filter(id__in=unique_menu_ids).count() != len(unique_menu_ids):
                return ErrorResponse(ErrCode.MENU_NOT_FOUND)
            if MenuButton.objects.filter(id__in=unique_button_ids).count() != len(unique_button_ids):
                return ErrorResponse(ErrCode.PARAM_ERROR)

            with transaction.atomic():
                AuthorityButton.objects.filter(authority=authority).delete()
                bound_buttons = set()
                for item in btn_data:
                    menu_id = item.get('menu_id')
                    button_ids = item.get('button_ids', [])
                    for button_id in button_ids:
                        if button_id in bound_buttons:
                            continue
                        bound_buttons.add(button_id)
                        AuthorityButton.objects.create(
                            authority=authority,
                            menu_id=menu_id,
                            button_id=button_id
                        )
            return SuccessResponse(errmsg='按钮权限绑定成功')

    @action(detail=True, methods=['post'], url_path='copy')
    def copy(self, request, pk=None):
        """复制角色"""
        authority = self.get_object()

        max_id = Authority.objects.order_by('-authority_id').first()
        new_authority_id = (max_id.authority_id + 1) if max_id else 1

        new_authority = Authority.objects.create(
            authority_id=new_authority_id,
            authority_name=f'{authority.authority_name}_副本',
            parent=authority.parent,
            default_router=authority.default_router,
            data_authority=authority.data_authority
        )

        menu_ids = AuthorityMenu.objects.filter(authority=authority).values_list('menu_id', flat=True)
        for menu_id in menu_ids:
            AuthorityMenu.objects.create(authority=new_authority, menu_id=menu_id)

        btn_relations = AuthorityButton.objects.filter(authority=authority)
        for rel in btn_relations:
            AuthorityButton.objects.create(
                authority=new_authority,
                menu=rel.menu,
                button=rel.button
            )

        return SuccessResponse({'id': new_authority.id}, errmsg='角色复制成功')


class MenuViewSet(UnifiedModelViewSet):
    """菜单管理视图集"""
    queryset = Menu.objects.all().order_by('sort')
    serializer_class = MenuSerializer
    permission_classes = [AuthorityPermission]

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
        return SuccessResponse(serializer.data)

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """批量更新菜单排序"""
        orders = request.data.get('orders', [])
        try:
            for item in orders:
                menu_id = item.get('id')
                sort = item.get('sort')
                Menu.objects.filter(id=menu_id).update(sort=sort)
            return SuccessResponse(errmsg='排序更新成功')
        except Exception as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e))
