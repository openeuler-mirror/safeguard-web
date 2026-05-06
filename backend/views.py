from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.http import HttpResponse
from pydantic import ValidationError

#  drf-spectacular 自动生成文档，无需手动写注解！
from drf_spectacular.utils import extend_schema

from backend.models import Users, EmailVerification
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
    SendVerificationCodeRequest,
    VerifyCodeRequest,
    RegisterWithCodeRequest,
    ForgotPasswordRequest,
    ResetPasswordWithCodeRequest,
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


class SendVerificationCodeView(APIView):
    """发送邮箱验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=SendVerificationCodeRequest,
        responses={200: MessageResponse, 400: MessageResponse},
        description="发送邮箱验证码"
    )
    def post(self, request):
        try:
            data = SendVerificationCodeRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        email = data.email

        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))

        # 验证码过期时间（10分钟）
        from django.conf import settings
        ttl_minutes = getattr(settings, 'EMAIL_VERIFICATION_CODE_TTL', 10)
        expires_at = timezone.now() + timedelta(minutes=ttl_minutes)

        # 保存验证码记录
        EmailVerification.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )

        # 检查是否为本地开发模式
        from django.conf import settings
        is_local = getattr(settings, 'IS_LOCAL', False)

        if is_local:
            # 本地模式：生成本地验证链接
            from django.conf import settings as django_settings
            backend_port = getattr(django_settings, 'BACKEND_PORT', 8000)
            local_url = f"http://localhost:{backend_port}/api/auth/local-verify/{email}/{code}/"
            return Response({
                "message": "本地验证模式",
                "local_verify_url": local_url,
                "code": code
            })

        # 发送邮件
        try:
            send_mail(
                subject='Safeguard 邮箱验证码',
                message=f'您的验证码是：{code}，{ttl_minutes}分钟内有效。',
                from_email=getattr(settings, 'EMAIL_FROM', None),
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"邮件发送失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "验证码已发送"})


class LocalVerifyView(APIView):
    """本地验证页面 - IS_LOCAL模式下显示验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, email, code):
        # 查找对应的验证码记录
        verification = EmailVerification.objects.filter(
            email=email,
            code=code,
            used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not verification:
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>验证码已失效</title>
                <style>
                    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f5f5f5; }
                    .container { text-align: center; padding: 40px; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
                    h2 { color: #f56c6c; }
                    p { color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>验证码已失效或不存在</h2>
                    <p>请返回重新发送验证码</p>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html)

        # 渲染验证页面
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>验证码 - Safeguard</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f5f5f5; }}
                .container {{ text-align: center; padding: 40px; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); max-width: 400px; }}
                h2 {{ color: #333; margin-bottom: 20px; }}
                .code-box {{ background: #e8f0fe; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .code {{ font-size: 32px; font-weight: bold; color: #409eff; letter-spacing: 8px; }}
                .info {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
                .copy-btn {{ background: #67c23a; color: white; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; margin-top: 10px; }}
                .copy-btn:hover {{ background: #85ce61; }}
                .hint {{ color: #909399; font-size: 12px; margin-top: 16px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>本地验证码</h2>
                <p class="info">开发模式下的验证码显示</p>
                <div class="code-box">
                    <div class="code" id="code">{code}</div>
                </div>
                <button class="copy-btn" onclick="copyCode()">复制验证码</button>
                <p class="hint">请返回注册页面输入验证码完成注册</p>
            </div>
            <script>
                function copyCode() {{
                    const code = document.getElementById('code').textContent;
                    navigator.clipboard.writeText(code).then(() => {{
                        const btn = document.querySelector('.copy-btn');
                        btn.textContent = '已复制!';
                        setTimeout(() => {{ btn.textContent = '复制验证码'; }}, 2000);
                    }});
                }}
            </script>
        </body>
        </html>
        """
        return HttpResponse(html)


class VerifyCodeView(APIView):
    """验证邮箱验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=VerifyCodeRequest,
        responses={200: MessageResponse, 400: MessageResponse},
        description="验证邮箱验证码"
    )
    def post(self, request):
        try:
            data = VerifyCodeRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        email = data.email
        code = data.code

        # 查找最新未使用的验证码
        verification = EmailVerification.objects.filter(
            email=email,
            code=code,
            used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not verification:
            return Response({"error": "验证码无效或已过期"}, status=status.HTTP_400_BAD_REQUEST)

        # 标记为已使用
        verification.used = True
        verification.save()

        return Response({"message": "验证成功"})


class ForgotPasswordView(APIView):
    """忘记密码 - 发送验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=ForgotPasswordRequest,
        responses={200: MessageResponse, 400: MessageResponse},
        description="忘记密码，发送验证码到邮箱"
    )
    def post(self, request):
        try:
            data = ForgotPasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        email = data.email

        # 检查该邮箱是否有注册用户
        user = Users.objects.filter(email=email).first()
        if not user:
            return Response({"error": "该邮箱未注册"}, status=status.HTTP_400_BAD_REQUEST)

        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))

        from django.conf import settings
        ttl_minutes = getattr(settings, 'EMAIL_VERIFICATION_CODE_TTL', 10)
        expires_at = timezone.now() + timedelta(minutes=ttl_minutes)

        # 保存验证码记录，关联到用户
        EmailVerification.objects.create(
            email=email,
            user=user,
            code=code,
            expires_at=expires_at
        )

        # 发送邮件
        try:
            send_mail(
                subject='Safeguard 密码重置验证码',
                message=f'您的验证码是：{code}，{ttl_minutes}分钟内有效。',
                from_email=getattr(settings, 'EMAIL_FROM', None),
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"邮件发送失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "验证码已发送"})


class ResetPasswordView(APIView):
    """通过验证码重置密码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=ResetPasswordWithCodeRequest,
        responses={200: MessageResponse, 400: MessageResponse},
        description="通过验证码重置密码"
    )
    def post(self, request):
        try:
            data = ResetPasswordWithCodeRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        email = data.email
        code = data.code
        new_password = data.new_password

        # 查找最新未使用的验证码
        verification = EmailVerification.objects.filter(
            email=email,
            code=code,
            used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not verification:
            return Response({"error": "验证码无效或已过期"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取关联用户
        user = verification.user
        if not user:
            return Response({"error": "用户不存在"}, status=status.HTTP_400_BAD_REQUEST)

        # 重置密码
        user.set_password(new_password)
        user.save()

        # 标记验证码已使用
        verification.used = True
        verification.save()

        return Response({"message": "密码重置成功"})
