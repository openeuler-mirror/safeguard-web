from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.hashers import make_password, check_password
from pydantic import ValidationError

from backend.models import Users
from backend.serializers import (
    UserSerializer,
    UserCreateSerializer,
)
from backend.schemas import (
    UserResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    SetRoleRequest,
    MessageResponse,
)


class UsersViewSet(viewsets.ModelViewSet):
    """用户管理视图集

    提供用户的增删改查功能，包括：
    - list: 获取用户列表
    - retrieve: 获取单个用户详情
    - create: 创建新用户
    - update: 更新用户信息
    - destroy: 删除用户
    """
    queryset = Users.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @swagger_auto_schema(
        methods=['get'],
        operation_description="获取当前登录用户的信息",
        responses={200: UserSerializer},
    )
    @swagger_auto_schema(
        methods=['put'],
        operation_description="更新当前登录用户的信息",
        request_body=UserUpdateRequest,
        responses={200: UserSerializer}, 
    )
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """GET/PUT /api/system/users/me/ - Current user info"""
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)
        elif request.method == 'PUT':
            # Pydantic validation
            try:
                UserUpdateRequest.model_validate(request.data)
            except ValidationError as e:
                return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="管理员重置用户密码",
        request_body=ResetPasswordRequest.model_json_schema(),
        responses={
            200: openapi.Response(description='密码重置成功', schema=MessageResponse.model_json_schema()),
            400: openapi.Response(description='请求参数错误'),
            404: openapi.Response(description='用户不存在')
        }
    )
    @action(detail=True, methods=['put'], url_path='password')
    def set_password(self, request, pk=None):
        """PUT /api/system/users/<id>/password/ - Admin reset password"""
        user = self.get_object()
        try:
            data = ResetPasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(data.new_password)
        user.save()
        return Response({"message": "密码重置成功"})

    @swagger_auto_schema(
        operation_description="用户修改自己的密码",
        request_body=ChangePasswordRequest.model_json_schema(),
        responses={
            200: openapi.Response(description='密码修改成功', schema=MessageResponse.model_json_schema()),
            400: openapi.Response(description='旧密码不正确或请求参数错误')
        }
    )
    @action(detail=False, methods=['put'], url_path='me/password')
    def change_my_password(self, request):
        """PUT /api/system/users/me/password/ - User change own password"""
        try:
            data = ChangePasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        if not check_password(data.old_password, request.user.password):
            return Response(
                {"error": "旧密码不正确"},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.set_password(data.new_password)
        request.user.save()
        return Response({"message": "密码修改成功"})

    @swagger_auto_schema(
        operation_description="管理员设置用户角色",
        request_body=SetRoleRequest.model_json_schema(),
        responses={
            200: openapi.Response(description='角色设置成功', schema=UserResponse.model_json_schema()),
            400: openapi.Response(description='role_id is required'),
            404: openapi.Response(description='角色不存在')
        }
    )
    @action(detail=True, methods=['put'], url_path='role')
    def set_role(self, request, pk=None):
        """PUT /api/system/users/<id>/role/ - Set user role"""
        return Response(
            {"error": "功能暂未实现"},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )