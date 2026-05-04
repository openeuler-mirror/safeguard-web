from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from backend.models import Users
from backend.serializers import (
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer
)


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet for SysUser CRUD"""
    queryset = Users.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """GET/PUT /api/system/users/me/ - Current user info"""
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)
        elif request.method == 'PUT':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='password')
    def set_password(self, request, pk=None):
        """PUT /api/system/users/<id>/password/ - Admin reset password"""
        user = self.get_object()
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.password = make_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "密码重置成功"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path='me/password')
    def change_my_password(self, request):
        """PUT /api/system/users/me/password/ - User change own password"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not check_password(serializer.validated_data['old_password'], request.user.password):
                return Response(
                    {"error": "旧密码不正确"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"message": "密码修改成功"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='role')
    def set_role(self, request, pk=None):
        """PUT /api/system/users/<id>/role/ - Set user role"""
        user = self.get_object()
        role_id = request.data.get('role_id')
        if not role_id:
            return Response(
                {"error": "role_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            role = SysRole.objects.get(id=role_id)
            user.role = role
            user.save()
            return Response(SysUserSerializer(user).data)
        except SysRole.DoesNotExist:
            return Response(
                {"error": "角色不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

