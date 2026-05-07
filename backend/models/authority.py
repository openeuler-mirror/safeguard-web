from django.db import models
from backend.models.user import Users


class Authority(models.Model):
    """角色主表"""
    authority_id = models.PositiveIntegerField(unique=True, verbose_name="角色ID")
    authority_name = models.CharField(max_length=100, verbose_name="角色名称")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="父角色", related_name="children"
    )
    default_router = models.CharField(max_length=255, default="dashboard", verbose_name="默认路由")
    data_authority = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="数据权限范围", related_name="data_scope"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sys_authorities"
        ordering = ["authority_id"]
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.authority_name


class Menu(models.Model):
    """动态菜单表"""
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        verbose_name="父菜单", related_name="children"
    )
    path = models.CharField(max_length=255, verbose_name="路由路径")
    name = models.CharField(max_length=100, verbose_name="路由名称")
    component = models.CharField(max_length=255, blank=True, verbose_name="前端组件路径")
    sort = models.IntegerField(default=0, verbose_name="排序")
    meta = models.JSONField(default=dict, verbose_name="菜单元数据")  # {title, icon}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sys_base_menus"
        ordering = ["sort"]
        verbose_name = "菜单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class MenuButton(models.Model):
    """菜单按钮表"""
    menu = models.ForeignKey(Menu, related_name="buttons", on_delete=models.CASCADE, verbose_name="所属菜单")
    name = models.CharField(max_length=100, verbose_name="按钮标识")  # add/edit/delete
    desc = models.CharField(max_length=255, blank=True, verbose_name="按钮描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sys_base_menu_btns"
        verbose_name = "菜单按钮"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.menu.name} - {self.name}"


class AuthorityMenu(models.Model):
    """角色-菜单关联表"""
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, verbose_name="角色")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="菜单")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sys_authority_menus"
        unique_together = ["authority", "menu"]
        verbose_name = "角色菜单关联"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.authority.authority_name} - {self.menu.name}"


class AuthorityButton(models.Model):
    """角色-按钮权限关联表"""
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, verbose_name="角色")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="菜单")
    button = models.ForeignKey(MenuButton, on_delete=models.CASCADE, verbose_name="按钮")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sys_authority_btns"
        unique_together = ["authority", "menu", "button"]
        verbose_name = "角色按钮权限"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.authority.authority_name} - {self.menu.name} - {self.button.name}"


class UserAuthority(models.Model):
    """用户-角色关联表 (N:N through table)"""
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="用户")
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, verbose_name="角色")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sys_user_authority"
        unique_together = ["user", "authority"]
        verbose_name = "用户角色关联"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.user} - {self.authority.authority_name}"
