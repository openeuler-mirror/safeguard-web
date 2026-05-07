"""自定义JWT认证，支持Redis校验"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token

from backend.authentication.redis_client import redis_client


class RedisJWTAuthentication(JWTAuthentication):
    """自定义JWT认证类，通过Redis校验用户状态"""

    def get_user(self, validated_token: Token):
        """
        从Redis获取用户状态，替代数据库查询
        """
        user_id = validated_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token无效，缺少user_id')

        user_key = f"user:{user_id}"

        # 从Redis获取用户数据
        user_data = redis_client.get(user_key)

        if user_data:
            import json
            user_info = json.loads(user_data)
        else:
            # Redis中没有用户数据，从数据库查询
            from backend.models import Users
            try:
                user = Users.objects.get(id=user_id)
                user_info = {
                    'id': user.id,
                    'uuid': str(user.uuid),
                    'user': user.user,
                    'nickname': user.nickname,
                    'enable': user.enable,
                    'password': user.password,
                }
            except Users.DoesNotExist:
                raise AuthenticationFailed('用户不存在')

        # 校验用户是否启用
        enable = user_info.get('enable', 1)
        if enable != 1:
            raise AuthenticationFailed('用户已被禁用')

        from backend.authentication.user import RedisUser
        return RedisUser(user_info)


__all__ = ['RedisJWTAuthentication']
