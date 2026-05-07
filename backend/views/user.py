from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from pydantic import ValidationError

from backend.models import Users, UserAuthority, Authority
from backend.serializers import UserSerializer, UserCreateSerializer
from backend.serializers.authority import MenuSerializer, UserAuthoritySerializer
from backend.schemas import UserUpdateRequest, ResetPasswordRequest, MessageResponse, UserResponse


class UsersViewSet(viewsets.ModelViewSet):
    """用户管理视图集
    提供用户的增删改查功能
    """
    queryset = Users.objects.all().order_by('-created_at')
    serializer_class = UserSerializer

    def get_permissions(self):
        """根据操作类型返回不同的权限"""
        if self.action in ['list', 'create', 'destroy', 'authorities', 'set_authorities', 'add_authority', 'remove_authority', 'set_password']:
            # 管理员操作，需要管理员权限（超级管理员或普通管理员）
            from backend.permissions import IsAdmin
            return [IsAdmin()]
        # 个人操作（me, menus, change_my_password）只需登录
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """获取/更新当前登录用户信息"""
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)

        try:
            UserUpdateRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'], url_path='menus')
    def menus(self, request):
        """获取当前用户可访问的菜单树"""
        from backend.models import Menu, AuthorityMenu
        from django.db.models import Prefetch

        # 获取用户关联的所有角色
        user_authorities = UserAuthority.objects.filter(user_id=request.user.id).values_list('authority_id', flat=True)

        # 获取这些角色关联的所有菜单
        menu_ids = AuthorityMenu.objects.filter(authority_id__in=user_authorities).values_list('menu_id', flat=True)

        # 获取菜单树
        root_menus = Menu.objects.filter(id__in=menu_ids, parent__isnull=True).prefetch_related(
            Prefetch('children', queryset=Menu.objects.filter(id__in=menu_ids).prefetch_related('children'))
        )

        serializer = MenuSerializer(root_menus, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='password')
    def set_password(self, request, pk=None):
        """管理员重置用户密码"""
        user = self.get_object()
        try:
            data = ResetPasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        user.password = make_password(data.new_password)
        user.save()
        return Response({"message": "密码重置成功"})

    @action(detail=False, methods=['put'], url_path='me/password')
    def change_my_password(self, request):
        """用户修改自己的密码"""
        from django.contrib.auth.hashers import check_password
        from backend.schemas import ChangePasswordRequest

        try:
            data = ChangePasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        if not check_password(data.old_password, request.user.password):
            return Response({"error": "旧密码不正确"}, status=400)

        request.user.set_password(data.new_password)
        request.user.save()
        return Response({"message": "密码修改成功"})

    @action(detail=True, methods=['get'], url_path='authorities')
    def authorities(self, request, pk=None):
        """获取指定用户的角色列表"""
        user = self.get_object()
        user_authorities = UserAuthority.objects.filter(user=user)
        serializer = UserAuthoritySerializer(user_authorities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='authorities')
    def set_authorities(self, request, pk=None):
        """设置用户角色（覆盖已有角色）"""
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])

        # 删除现有角色关联
        UserAuthority.objects.filter(user=user).delete()

        # 创建新角色关联
        for role_id in role_ids:
            try:
                authority = Authority.objects.get(pk=role_id)
                UserAuthority.objects.create(user=user, authority=authority)
            except Authority.DoesNotExist:
                pass

        return Response({"message": "角色设置成功"})

    @action(detail=True, methods=['post'], url_path='authorities/add')
    def add_authority(self, request, pk=None):
        """为用户添加角色"""
        user = self.get_object()
        authority_id = request.data.get('authority_id')

        if not authority_id:
            return Response({"error": "authority_id 不能为空"}, status=400)

        try:
            authority = Authority.objects.get(pk=authority_id)
        except Authority.DoesNotExist:
            return Response({"error": "角色不存在"}, status=400)

        user_authority, created = UserAuthority.objects.get_or_create(user=user, authority=authority)
        if not created:
            return Response({"error": "用户已有该角色"}, status=400)

        serializer = UserAuthoritySerializer(user_authority)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['delete'], url_path='authorities')
    def remove_authority(self, request, pk=None):
        """移除用户角色"""
        user = self.get_object()
        authority_id = request.data.get('authority_id')

        if not authority_id:
            return Response({"error": "authority_id 不能为空"}, status=400)

        try:
            user_authority = UserAuthority.objects.get(user=user, authority_id=authority_id)
            user_authority.delete()
        except UserAuthority.DoesNotExist:
            return Response({"error": "用户没有该角色"}, status=400)

        return Response({"message": "角色移除成功"})
