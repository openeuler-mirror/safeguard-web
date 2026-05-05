from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password, check_password
from pydantic import ValidationError

#  drf-spectacular 自动生成文档，无需手动写注解！
from drf_spectacular.utils import extend_schema

from backend.models import Users
from backend.serializers import UserSerializer, UserCreateSerializer
# 你的 Pydantic Schema（全部保留）
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
    提供用户的增删改查功能
    """
    queryset = Users.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    # ==============================================
    # 个人信息接口（GET查询 / PUT更新）
    # Pydantic 校验 + Swagger 自动生成文档
    # ==============================================
    @extend_schema(
        methods=['get'],
        responses={200: UserResponse},
        description="获取当前登录用户信息"
    )
    @extend_schema(
        methods=['post'],
        request=UserUpdateRequest,
        responses={200: UserResponse, 400: MessageResponse},
        description="更新当前登录用户信息"
    )
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)

        # PUT：Pydantic 严格参数校验
        try:
            UserUpdateRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ==============================================
    # 管理员重置密码
    # ==============================================
    @extend_schema(
        request=ResetPasswordRequest,
        responses={200: MessageResponse, 400: MessageResponse},
        description="管理员重置用户密码"
    )
    @action(detail=True, methods=['put'], url_path='password')
    def set_password(self, request, pk=None):
        user = self.get_object()
        try:
            data = ResetPasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(data.new_password)
        user.save()
        return Response({"message": "密码重置成功"})

    # ==============================================
    # 用户修改自身密码
    # ==============================================
    @extend_schema(
        request=ChangePasswordRequest,
        responses={200: MessageResponse, 400: MessageResponse},
        description="用户修改自己的密码"
    )
    @action(detail=False, methods=['put'], url_path='me/password')
    def change_my_password(self, request):
        try:
            data = ChangePasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        if not check_password(data.old_password, request.user.password):
            return Response({"error": "旧密码不正确"}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(data.new_password)
        request.user.save()
        return Response({"message": "密码修改成功"})

    # ==============================================
    # 管理员设置用户角色
    # ==============================================
    @extend_schema(
        request=SetRoleRequest,
        responses={200: UserResponse, 400: MessageResponse},
        description="管理员设置用户角色"
    )
    @action(detail=True, methods=['put'], url_path='role')
    def set_role(self, request, pk=None):
        return Response({"error": "功能暂未实现"}, status=status.HTTP_501_NOT_IMPLEMENTED)
