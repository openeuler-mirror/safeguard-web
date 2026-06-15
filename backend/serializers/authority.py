from rest_framework import serializers
from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority


class MenuButtonSerializer(serializers.ModelSerializer):
    """菜单按钮序列化器"""
    class Meta:
        model = MenuButton
        fields = ['id', 'menu', 'name', 'desc', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MenuSerializer(serializers.ModelSerializer):
    """菜单序列化器"""
    buttons = MenuButtonSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'parent', 'path', 'name', 'component', 'sort', 'meta', 'description', 'buttons', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MenuUpdateSerializer(serializers.ModelSerializer):
    """菜单更新序列化器（部分字段可更新）"""
    path = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = Menu
        fields = ['parent', 'path', 'name', 'component', 'sort', 'meta']


class MenuTreeSerializer(serializers.ModelSerializer):
    """菜单树序列化器（嵌套子菜单）"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'parent', 'path', 'name', 'component', 'sort', 'meta', 'description', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return MenuTreeSerializer(children, many=True).data


class AuthoritySerializer(serializers.ModelSerializer):
    """角色序列化器"""
    parent_name = serializers.CharField(source='parent.authority_name', read_only=True)
    data_authority_name = serializers.CharField(source='data_authority.authority_name', read_only=True)

    class Meta:
        model = Authority
        fields = [
            'id', 'authority_id', 'authority_name', 'parent', 'parent_name',
            'default_router', 'data_authority', 'data_authority_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuthorityCreateSerializer(serializers.ModelSerializer):
    """角色创建序列化器"""
    class Meta:
        model = Authority
        fields = ['authority_id', 'authority_name', 'parent', 'default_router', 'data_authority']


class AuthorityUpdateSerializer(serializers.ModelSerializer):
    """角色更新序列化器"""
    class Meta:
        model = Authority
        fields = ['authority_name', 'parent', 'default_router', 'data_authority']


class AuthorityMenuSerializer(serializers.ModelSerializer):
    """角色-菜单关联序列化器"""
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    authority_name = serializers.CharField(source='authority.authority_name', read_only=True)

    class Meta:
        model = AuthorityMenu
        fields = ['id', 'authority', 'authority_name', 'menu', 'menu_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuthorityButtonSerializer(serializers.ModelSerializer):
    """角色-按钮权限序列化器"""
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    button_name = serializers.CharField(source='button.name', read_only=True)
    authority_name = serializers.CharField(source='authority.authority_name', read_only=True)

    class Meta:
        model = AuthorityButton
        fields = ['id', 'authority', 'authority_name', 'menu', 'menu_name', 'button', 'button_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserAuthoritySerializer(serializers.ModelSerializer):
    """用户-角色关联序列化器"""
    user_username = serializers.CharField(source='user.user', read_only=True)
    authority_name = serializers.CharField(source='authority.authority_name', read_only=True)

    class Meta:
        model = UserAuthority
        fields = ['id', 'user', 'user_username', 'authority', 'authority_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class SetUserRoleSerializer(serializers.Serializer):
    """设置用户角色请求序列化器"""
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="角色ID列表"
    )
