from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
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
    LoginRequest,
    TokenResponse,
)


class UsersViewSet(viewsets.ModelViewSet):
    """用户管理视图集
    提供用户的增删改查功能
    """
    queryset = Users.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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
        methods=['put'],
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


class LoginView(APIView):
    """用户登录接口"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=LoginRequest,
        responses={200: TokenResponse, 400: MessageResponse, 401: MessageResponse},
        description="用户登录，返回JWT token"
    )
    def post(self, request):
        try:
            data = LoginRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        # 手动查找用户并验证（不使用django默认authenticate）
        try:
            user = Users.objects.get(user=data.username)
        except Users.DoesNotExist:
            return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(data.password, user.password):
            return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "用户已被禁用"}, status=status.HTTP_401_UNAUTHORIZED)

        # 生成JWT token
        refresh = RefreshToken.for_user(user)

        return Response(TokenResponse(
            access=str(refresh.access_token),
            refresh=str(refresh)
        ).model_dump())


class RegisterView(APIView):
    """用户注册接口"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request={
            "type": "object",
            "properties": {
                "user": {"type": "string", "description": "用户名"},
                "password": {"type": "string", "description": "密码"},
                "nickname": {"type": "string", "description": "昵称（可选）"},
                "phone": {"type": "string", "description": "手机号（可选）"},
                "email": {"type": "string", "description": "邮箱（可选）"}
            },
            "required": ["user", "password"]
        },
        responses={201: UserResponse, 400: MessageResponse},
        description="用户注册"
    )
    def put(self, request):
        user = request.data.get('user')
        password = request.data.get('password')

        if not user or not password:
            return Response({"error": "用户名和密码不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({"error": "密码长度至少6位"}, status=status.HTTP_400_BAD_REQUEST)

        if Users.objects.filter(user=user).exists():
            return Response({"error": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)

        nickname = request.data.get('nickname', '系统用户')
        phone = request.data.get('phone', '')
        email = request.data.get('email', '')

        new_user = Users(user=user, nickname=nickname, phone=phone, email=email)
        new_user.set_password(password)
        new_user.save()

        return Response(UserSerializer(new_user).data, status=status.HTTP_201_CREATED)
