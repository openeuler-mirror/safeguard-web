"""
初始化 Authority 模块数据

用法：
    python manage.py init_authority
"""
from django.core.management.base import BaseCommand
from backend.models import Authority, Menu, MenuButton, AuthorityMenu


class Command(BaseCommand):
    help = '初始化 Authority 模块的默认角色和菜单数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化 Authority 数据...\n')

        # 1. 创建默认角色
        self.create_authorities()

        # 2. 创建默认菜单
        self.create_menus()

        # 3. 绑定超级管理员菜单
        self.bind_admin_menus()

        self.stdout.write(self.style.SUCCESS('\n初始化完成！'))

    def create_authorities(self):
        """创建默认角色"""
        authorities_data = [
            {
                'authority_id': 888,
                'authority_name': '超级管理员',
                'parent': None,
                'default_router': 'dashboard',
                'data_authority': None,
            },
            {
                'authority_id': 889,
                'authority_name': '普通管理员',
                'parent': None,
                'default_router': 'dashboard',
                'data_authority': None,
            },
            {
                'authority_id': 890,
                'authority_name': '普通用户',
                'parent': None,
                'default_router': 'dashboard',
                'data_authority': None,
            },
        ]

        created_count = 0
        for data in authorities_data:
            authority, created = Authority.objects.get_or_create(
                authority_id=data['authority_id'],
                defaults={
                    'authority_name': data['authority_name'],
                    'parent': data['parent'],
                    'default_router': data['default_router'],
                    'data_authority': data['data_authority'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  创建角色: {authority.authority_name} (ID: {authority.authority_id})')
            else:
                self.stdout.write(f'  角色已存在: {authority.authority_name} (ID: {authority.authority_id})')

        self.stdout.write(f'角色创建完成: {created_count} 个新角色\n')

    def create_menus(self):
        """创建默认菜单"""
        menus_data = [
            {
                'name': 'Dashboard',
                'path': '/dashboard',
                'component': '/dashboard/index.vue',
                'sort': 1,
                'meta': {'title': '仪表盘', 'icon': 'dashboard'},
            },
            {
                'name': 'UserManagement',
                'path': '/users',
                'component': '/users/index.vue',
                'sort': 10,
                'meta': {'title': '用户管理', 'icon': 'user'},
            },
            {
                'name': 'AuthorityManagement',
                'path': '/authorities',
                'component': '/authorities/index.vue',
                'sort': 20,
                'meta': {'title': '角色管理', 'icon': ' authority'},
            },
            {
                'name': 'MenuManagement',
                'path': '/menus',
                'component': '/menus/index.vue',
                'sort': 21,
                'meta': {'title': '菜单管理', 'icon': 'menu'},
            },
            {
                'name': 'HostManagement',
                'path': '/hosts',
                'component': '/hosts/index.vue',
                'sort': 30,
                'meta': {'title': '主机管理', 'icon': 'host'},
            },
        ]

        created_count = 0
        for data in menus_data:
            menu, created = Menu.objects.get_or_create(
                path=data['path'],
                defaults={
                    'name': data['name'],
                    'component': data['component'],
                    'sort': data['sort'],
                    'meta': data['meta'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  创建菜单: {menu.name} (路径: {menu.path})')
            else:
                self.stdout.write(f'  菜单已存在: {menu.name} (路径: {menu.path})')

        self.stdout.write(f'菜单创建完成: {created_count} 个新菜单\n')

    def bind_admin_menus(self):
        """绑定超级管理员菜单"""
        try:
            admin_authority = Authority.objects.get(authority_id=888)
        except Authority.DoesNotExist:
            self.stdout.write(self.style.ERROR('  超级管理员角色不存在，跳过菜单绑定\n'))
            return

        # 获取所有菜单
        all_menus = Menu.objects.all()

        # 获取已绑定的菜单
        bound_menu_ids = AuthorityMenu.objects.filter(authority=admin_authority).values_list('menu_id', flat=True)

        # 绑定未绑定的菜单
        created_count = 0
        for menu in all_menus:
            if menu.id not in bound_menu_ids:
                AuthorityMenu.objects.create(authority=admin_authority, menu=menu)
                created_count += 1
                self.stdout.write(f'  绑定菜单到超级管理员: {menu.name}')

        self.stdout.write(f'菜单绑定完成: {created_count} 个菜单已绑定到超级管理员\n')
