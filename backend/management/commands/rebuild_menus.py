"""
重建系统菜单树

用法：
    python manage.py rebuild_menus

说明：
    1. 删除现有菜单
    2. 按标准层级重建所有菜单（仪表盘、用户/角色/菜单管理、集群/主机/镜像/虚拟机、
       OS 部署、网络 LB、安全部署、任务中心、系统迁移）
    3. 将重建后的所有菜单绑定到超级管理员角色（authority_id=888）
    4. 将仪表盘和用户管理绑定到普通管理员角色（authority_id=889）

注意：此命令会清空现有菜单及角色-菜单关联，请在首次部署或菜单结构需要重置时使用。
"""
from django.core.management.base import BaseCommand
from backend.models import Menu, Authority, AuthorityMenu


class Command(BaseCommand):
    help = '重建系统菜单树并重新绑定角色权限'

    def handle(self, *args, **options):
        self.stdout.write('开始重建菜单树...')

        Menu.objects.all().delete()
        AuthorityMenu.objects.all().delete()

        def create_menu(name, path, sort, parent=None, component='', description=''):
            return Menu.objects.create(
                name=name,
                path=path,
                sort=sort,
                parent=parent,
                component=component,
                meta={'title': name, 'icon': 'app'},
                description=description,
            )

        # 一级菜单
        dashboard = create_menu('仪表盘', '/dashboard', 1, component='/dashboard/index.vue')
        users = create_menu('用户管理', '/users', 10, component='/users/index.vue')
        create_menu('角色管理', '/authorities', 20, component='/authorities/index.vue')
        create_menu('菜单管理', '/menus', 21, component='/menus/index.vue')
        create_menu('集群管理', '/clusters', 25, component='/clusters/index.vue')
        hosts = create_menu('主机管理', '/hosts', 30, component='/hosts/index.vue')
        create_menu('镜像管理', '/images', 32, component='/images/index.vue')
        create_menu('虚拟机管理', '/vms', 33, component='/vms/index.vue')

        # 系统安装
        osdeploy = create_menu('系统安装', '/osdeploy', 40)
        create_menu('安装任务', '/osdeploy/jobs', 1, osdeploy, '/osdeploy/jobs/index.vue')
        create_menu('安装源仓库', '/osdeploy/repos', 2, osdeploy, '/osdeploy/repos/index.vue')
        create_menu('自动应答配置', '/osdeploy/kickstarts', 3, osdeploy, '/osdeploy/kickstarts/index.vue')
        create_menu('网络启动配置', '/osdeploy/pxe', 4, osdeploy, '/osdeploy/pxe/index.vue')
        create_menu('自动安装', '/osdeploy/auto-install', 5, osdeploy, '/osdeploy/auto-install/index.vue')
        create_menu('安装白名单', '/osdeploy/whitelist', 6, osdeploy, '/osdeploy/whitelist/index.vue')
        create_menu('系统镜像', '/osdeploy/isos', 7, osdeploy, '/osdeploy/isos/index.vue')
        create_menu('资产序列号绑定', '/osdeploy/outipsn', 8, osdeploy, '/osdeploy/outipsn/index.vue')

        # 网络负载均衡
        network = create_menu('网络负载均衡', '/network', 50)
        create_menu('负载均衡器', '/network/lbs', 1, network, '/network/lbs/index.vue')
        create_menu('监听器', '/network/listeners', 2, network, '/network/listeners/index.vue')
        create_menu('后端服务器组', '/network/pools', 3, network, '/network/pools/index.vue')
        create_menu('服务器成员', '/network/members', 4, network, '/network/members/index.vue')
        create_menu('健康检查', '/network/health-monitors', 5, network, '/network/health-monitors/index.vue')

        # 安全部署
        security = create_menu('安全部署', '/security', 60)
        create_menu('安全任务', '/security/safeguards', 1, security, '/security/safeguards/index.vue')

        # 任务中心
        tasks = create_menu('任务中心', '/tasks', 70, component='/tasks/index.vue')

        # 系统迁移
        osmigrate = create_menu('系统迁移', '/osmigrate', 80)
        create_menu('迁移任务', '/osmigrate/migrations', 1, osmigrate, '/osmigrate/migrations/index.vue')

        # 绑定角色
        super_admin = Authority.objects.get(authority_id=888)
        normal_admin = Authority.objects.get(authority_id=889)

        for menu in Menu.objects.all():
            AuthorityMenu.objects.create(authority=super_admin, menu=menu)

        for menu in [dashboard, users]:
            AuthorityMenu.objects.create(authority=normal_admin, menu=menu)

        self.stdout.write(self.style.SUCCESS(f'菜单重建完成，共 {Menu.objects.count()} 个菜单'))
