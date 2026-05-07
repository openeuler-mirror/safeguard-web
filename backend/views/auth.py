from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponse
from pydantic import ValidationError
import random
import string

from backend.models import Users, EmailVerification, Authority, UserAuthority
from backend.serializers import UserSerializer
from backend.schemas import (
    LoginRequest, TokenResponse, MessageResponse,
    SendVerificationCodeRequest, VerifyCodeRequest,
    ForgotPasswordRequest, ResetPasswordWithCodeRequest,
)
from safeguard_web.settings import (
    IS_LOCAL, EMAIL_CODE_COOLDOWN, EMAIL_VERIFICATION_CODE_TTL,
    BACKEND_PORT, EMAIL_FROM, DEFAULT_USER_AUTHORITY_ID
)


class LoginView(APIView):
    """用户登录接口"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            data = LoginRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        # 手动查找用户并验证（支持用户名或邮箱登录）
        user = None
        if Users.objects.filter(user=data.username).exists():
            user = Users.objects.get(user=data.username)
        elif Users.objects.filter(email=data.username).exists():
            user = Users.objects.get(email=data.username)

        if not user:
            return Response({"error": "用户名或密码错误"}, status=401)

        if not check_password(data.password, user.password):
            return Response({"error": "用户名或密码错误"}, status=401)

        if not user.is_active:
            return Response({"error": "用户已被禁用"}, status=401)

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

    def put(self, request):
        user = request.data.get('user')
        password = request.data.get('password')

        if not user or not password:
            return Response({"error": "用户名和密码不能为空"}, status=400)

        if len(password) < 6:
            return Response({"error": "密码长度至少6位"}, status=400)

        if Users.objects.filter(user=user).exists():
            return Response({"error": "用户名已存在"}, status=400)

        nickname = request.data.get('nickname', '系统用户')
        phone = request.data.get('phone', '')
        email = request.data.get('email', '')

        new_user = Users(user=user, nickname=nickname, phone=phone, email=email)
        new_user.set_password(password)
        new_user.save()

        # 自动分配默认角色
        try:
            default_authority = Authority.objects.get(authority_id=DEFAULT_USER_AUTHORITY_ID)
            UserAuthority.objects.create(user=new_user, authority=default_authority)
        except Authority.DoesNotExist:
            pass

        return Response(UserSerializer(new_user).data, status=201)


class SendVerificationCodeView(APIView):
    """发送邮箱验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            data = SendVerificationCodeRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        email = data.email
        user = None

        if data.purpose == 'register':
            if Users.objects.filter(email=email).exists():
                return Response({"error": "该邮箱已被注册"}, status=400)
        elif data.purpose == 'forgot':
            user = Users.objects.filter(email=email).first()
            if not user:
                return Response({"error": "该邮箱未注册"}, status=400)

        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=EMAIL_VERIFICATION_CODE_TTL)

        EmailVerification.objects.create(
            email=email,
            user=user,
            code=code,
            expires_at=expires_at
        )

        if IS_LOCAL:
            local_url = f"http://localhost:{BACKEND_PORT}/api/auth/local-verify/{email}/{code}/"
            return Response({
                "message": "本地验证模式",
                "local_verify_url": local_url,
                "code": code
            })

        try:
            send_mail(
                subject='Safeguard 邮箱验证码',
                message=f'您的验证码是：{code}，{EMAIL_VERIFICATION_CODE_TTL}分钟内有效。',
                from_email=EMAIL_FROM,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"邮件发送失败: {str(e)}"}, status=500)

        return Response({"message": "验证码已发送"})


class LocalVerifyView(APIView):
    """本地验证页面 - IS_LOCAL模式下显示验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, email, code):
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

    def post(self, request):
        try:
            data = VerifyCodeRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        email = data.email
        code = data.code

        verification = EmailVerification.objects.filter(
            email=email,
            code=code,
            used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not verification:
            return Response({"error": "验证码无效或已过期"}, status=400)

        verification.used = True
        verification.save()

        return Response({"message": "验证成功"})


class ForgotPasswordView(APIView):
    """忘记密码 - 发送验证码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            data = ForgotPasswordRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        email = data.email

        user = Users.objects.filter(email=email).first()
        if not user:
            return Response({"error": "该邮箱未注册"}, status=400)

        code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=EMAIL_VERIFICATION_CODE_TTL)

        EmailVerification.objects.create(
            email=email,
            user=user,
            code=code,
            expires_at=expires_at
        )

        if IS_LOCAL:
            local_url = f"http://localhost:{BACKEND_PORT}/api/auth/local-verify/{email}/{code}/"
            return Response({
                "message": "本地验证模式",
                "local_verify_url": local_url,
                "code": code
            })

        try:
            send_mail(
                subject='Safeguard 密码重置验证码',
                message=f'您的验证码是：{code}，{EMAIL_VERIFICATION_CODE_TTL}分钟内有效。',
                from_email=EMAIL_FROM,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"邮件发送失败: {str(e)}"}, status=500)

        return Response({"message": "验证码已发送"})


class ResetPasswordView(APIView):
    """通过验证码重置密码"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            data = ResetPasswordWithCodeRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=400)

        email = data.email
        code = data.code
        new_password = data.new_password

        verification = EmailVerification.objects.filter(
            email=email,
            code=code,
            used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not verification:
            return Response({"error": "验证码无效或已过期"}, status=400)

        user = verification.user
        if not user:
            return Response({"error": "用户不存在"}, status=400)

        user.set_password(new_password)
        user.save()

        verification.used = True
        verification.save()

        return Response({"message": "密码重置成功"})
