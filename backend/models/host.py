from django.db import models


class Cluster(models.Model):
    """集群"""
    name = models.CharField(max_length=100, unique=True, verbose_name="集群名称")
    description = models.TextField(blank=True, verbose_name="描述")
    vcenter_id = models.CharField(max_length=100, blank=True, verbose_name="vCenter ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "clusters"
        ordering = ['id']
        verbose_name = "集群"
        verbose_name_plural = verbose_name


class Host(models.Model):
    """宿主机"""

    # 基本信息
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="序列号")
    hostname = models.CharField(max_length=255, verbose_name="主机名")
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="管理IP")
    port = models.IntegerField(default=22, verbose_name="SSH端口")
    username = models.CharField(max_length=50, verbose_name="用户名")
    password = models.CharField(max_length=255, blank=True, verbose_name="密码（加密存储）")

    # 关联信息
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属集群")
    cluster_name = models.CharField(max_length=100, blank=True, verbose_name="集群名称")

    # 状态信息
    status = models.CharField(max_length=20, choices=[("online", "在线"), ("offline", "离线")], default="offline")
    os_type = models.CharField(max_length=50, blank=True, verbose_name="操作系统")
    host_type = models.CharField(max_length=50, default="VMHost", verbose_name="设备分类")

    # 使用信息
    use_name = models.CharField(max_length=100, blank=True, verbose_name="使用人")
    use_for = models.CharField(max_length=100, blank=True, verbose_name="用途")

    # 网络配置 - 管理网络
    netmask = models.CharField(max_length=20, blank=True, verbose_name="管理网络掩码")
    bond_type = models.CharField(max_length=20, blank=True, verbose_name="Bond模式")
    manage_vlan = models.CharField(max_length=20, blank=True, verbose_name="管理VLAN")
    manage_nic1 = models.CharField(max_length=50, blank=True, verbose_name="管理网卡1")
    manage_nic2 = models.CharField(max_length=50, blank=True, verbose_name="管理网卡2")
    manage_address_ipv6 = models.GenericIPAddressField(null=True, blank=True, verbose_name="管理IPv6地址")
    manage_netmask_ipv6 = models.CharField(max_length=20, blank=True, verbose_name="管理IPv6掩码")

    # IPMI 配置
    ipmi_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IPMI地址")
    ipmi_user = models.CharField(max_length=50, blank=True, verbose_name="IPMI用户名")
    ipmi_password = models.CharField(max_length=100, blank=True, verbose_name="IPMI密码")
    ipmi_vlan = models.CharField(max_length=20, blank=True, verbose_name="IPMI VLAN")

    # 网络配置 - 存储网络
    storage_vlan = models.CharField(max_length=20, blank=True, verbose_name="存储VLAN")
    storage_ifname = models.CharField(max_length=50, blank=True, verbose_name="存储接口名称")
    storage_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="存储IP地址")
    storage_netmask = models.CharField(max_length=20, blank=True, verbose_name="存储网络掩码")

    # 网络配置 - 业务网络
    business_vlan = models.CharField(max_length=20, blank=True, verbose_name="业务VLAN")
    business_ifname = models.CharField(max_length=50, blank=True, verbose_name="业务接口名称")
    business_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="业务IP地址")
    business_netmask = models.CharField(max_length=20, blank=True, verbose_name="业务网络掩码")
    business_bond_type = models.CharField(max_length=20, blank=True, verbose_name="业务Bond模式")
    business_nic1 = models.CharField(max_length=50, blank=True, verbose_name="业务网卡1")
    business_nic2 = models.CharField(max_length=50, blank=True, verbose_name="业务网卡2")

    # 网络配置 - 其他网络
    other_vlan = models.CharField(max_length=20, blank=True, verbose_name="其他VLAN")
    other_ifname = models.CharField(max_length=50, blank=True, verbose_name="其他接口名称")
    other_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="其他IP地址")
    other_netmask = models.CharField(max_length=20, blank=True, verbose_name="其他网络掩码")
    other_nic1 = models.CharField(max_length=50, blank=True, verbose_name="其他网卡1")
    other_nic2 = models.CharField(max_length=50, blank=True, verbose_name="其他网卡2")

    # 属性标志
    is_cluster_type = models.BooleanField(default=False, verbose_name="是否有集群属性")
    is_zone_type = models.BooleanField(default=False, verbose_name="是否有专区属性")
    is_bind_cell_type = models.BooleanField(default=False, verbose_name="是否绑定cell")
    flag = models.BooleanField(default=True, verbose_name="标记")

    # 硬件信息
    raid = models.CharField(max_length=100, blank=True, verbose_name="RAID配置")
    bios_config = models.TextField(blank=True, verbose_name="BIOS配置要求")
    asset_number = models.CharField(max_length=100, blank=True, verbose_name="资产编号")
    is_warranty_period = models.BooleanField(default=False, verbose_name="是否在保修期")
    server_brand = models.CharField(max_length=100, blank=True, verbose_name="服务器品牌")
    server_model = models.CharField(max_length=100, blank=True, verbose_name="服务器型号")
    server_size = models.CharField(max_length=100, blank=True, verbose_name="服务器大小")
    base_location = models.CharField(max_length=100, blank=True, verbose_name="基地")
    server_room_number = models.CharField(max_length=100, blank=True, verbose_name="机房编号")
    cabinet_number = models.CharField(max_length=100, blank=True, verbose_name="机柜编号")

    # LLDP 信息
    lldp_infos = models.JSONField(default=list, verbose_name="LLDP信息")

    # 集群属性
    cell_vip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Cell VIP")
    ntp_address = models.CharField(max_length=100, blank=True, verbose_name="NTP地址")

    # 采集的硬件信息
    arch_info = models.TextField(blank=True, verbose_name="内核架构信息")
    os_version = models.TextField(blank=True, verbose_name="操作系统版本")
    uptime = models.CharField(max_length=100, blank=True, verbose_name="运行时间")
    cpu_info = models.TextField(blank=True, verbose_name="CPU信息")
    disk_info = models.TextField(blank=True, verbose_name="磁盘信息")
    memory_info = models.CharField(max_length=100, blank=True, verbose_name="内存信息")
    network_info = models.TextField(blank=True, verbose_name="网络信息")
    mount_info = models.TextField(blank=True, verbose_name="mount信息")
    dmesg_info = models.TextField(blank=True, verbose_name="dmesg信息")

    # 其他信息
    mac_address = models.CharField(max_length=17, blank=True, verbose_name="MAC地址")
    region = models.CharField(max_length=100, blank=True, verbose_name="区域")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

    class Meta:
        db_table = "hosts"
        ordering = ['id']
        verbose_name = "宿主机"
        verbose_name_plural = verbose_name


class VM(models.Model):
    """虚拟机"""

    STATUS_CHOICES = [
        ("stopped", "已停止"),
        ("running", "运行中"),
        ("paused", "暂停"),
        ("suspended", "挂起"),
    ]

    # 基本信息
    name = models.CharField(max_length=255, verbose_name="VM名称")
    uuid = models.CharField(max_length=100, unique=True, verbose_name="UUID")
    mac_address = models.CharField(max_length=17, blank=True, verbose_name="MAC地址")

    # 关联信息
    host = models.ForeignKey(Host, related_name="vms", on_delete=models.CASCADE, verbose_name="所属宿主机")
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属集群")

    # 资源配置
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="stopped", verbose_name="状态")
    vcpu = models.IntegerField(default=1, verbose_name="虚拟CPU核数")
    memory = models.BigIntegerField(default=0, verbose_name="内存(字节)")
    disk = models.BigIntegerField(default=0, verbose_name="磁盘(字节)")

    # 网络配置
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    management_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="管理IP")
    storage_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="存储IP")

    # 系统信息
    os_type = models.CharField(max_length=50, blank=True, verbose_name="操作系统")

    # 虚拟机配置
    vm_image_path = models.CharField(max_length=255, blank=True, verbose_name="虚拟机镜像路径")
    vm_disk_path = models.CharField(max_length=255, blank=True, verbose_name="虚拟机磁盘路径")
    vm_network_bridge = models.CharField(max_length=50, blank=True, verbose_name="虚拟机网桥")

    # oskit 扩展字段
    imageid = models.CharField(max_length=100, blank=True, verbose_name="镜像ID")
    sysdisk = models.JSONField(default=dict, blank=True, verbose_name="系统盘信息")
    datadisk = models.JSONField(default=list, blank=True, verbose_name="数据盘信息")
    status_message = models.CharField(max_length=255, blank=True, verbose_name="状态消息")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address or 'No IP'})"

    class Meta:
        db_table = "vms"
        ordering = ['id']
        verbose_name = "虚拟机"
        verbose_name_plural = verbose_name


class Image(models.Model):
    """虚拟机镜像"""

    # 基本信息
    id = models.CharField(max_length=100, primary_key=True, verbose_name="镜像ID")
    name = models.CharField(max_length=255, verbose_name="镜像名称")
    ostype = models.CharField(max_length=50, blank=True, verbose_name="操作系统类型")
    path = models.CharField(max_length=255, verbose_name="镜像路径")

    # 关联信息
    host = models.ForeignKey(Host, on_delete=models.CASCADE, verbose_name="所属宿主机")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ostype})"

    class Meta:
        db_table = "images"
        ordering = ['id']
        verbose_name = "虚拟机镜像"
        verbose_name_plural = verbose_name