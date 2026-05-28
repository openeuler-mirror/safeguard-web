from rest_framework import serializers
from backend.models.host import Cluster, Host, VM, Image


class ClusterSerializer(serializers.ModelSerializer):
    """集群序列化器"""
    host_count = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'description', 'vcenter_id', 'host_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_host_count(self, obj):
        return obj.host_set.count()


class ClusterCreateSerializer(serializers.ModelSerializer):
    """集群创建序列化器"""
    class Meta:
        model = Cluster
        fields = ['name', 'description', 'vcenter_id']


class ClusterUpdateSerializer(serializers.ModelSerializer):
    """集群更新序列化器"""
    class Meta:
        model = Cluster
        fields = ['name', 'description', 'vcenter_id']


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器（完整信息）"""
    cluster_name = serializers.CharField(source='cluster.name', read_only=True, allow_null=True)

    class Meta:
        model = Host
        fields = [
            'id', 'serial_number', 'hostname', 'ip_address', 'port', 'username',
            'cluster', 'cluster_name', 'status', 'os_type', 'host_type',
            'use_name', 'use_for',
            'netmask', 'bond_type', 'manage_vlan', 'manage_nic1', 'manage_nic2',
            'manage_address_ipv6', 'manage_netmask_ipv6',
            'ipmi_address', 'ipmi_user', 'ipmi_password', 'ipmi_vlan',
            'storage_vlan', 'storage_ifname', 'storage_address', 'storage_netmask',
            'business_vlan', 'business_ifname', 'business_address', 'business_netmask',
            'business_bond_type', 'business_nic1', 'business_nic2',
            'other_vlan', 'other_ifname', 'other_address', 'other_netmask',
            'other_nic1', 'other_nic2',
            'is_cluster_type', 'is_zone_type', 'is_bind_cell_type', 'flag',
            'raid', 'bios_config', 'asset_number', 'is_warranty_period',
            'server_brand', 'server_model', 'server_size',
            'base_location', 'server_room_number', 'cabinet_number',
            'lldp_infos', 'cell_vip', 'ntp_address',
            'arch_info', 'os_version', 'uptime', 'cpu_info', 'disk_info',
            'memory_info', 'network_info', 'mount_info', 'dmesg_info',
            'mac_address', 'region',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HostCreateSerializer(serializers.ModelSerializer):
    """主机创建序列化器"""
    class Meta:
        model = Host
        fields = [
            'serial_number', 'hostname', 'ip_address', 'port', 'username', 'password',
            'cluster', 'status', 'os_type', 'host_type',
            'use_name', 'use_for',
            'netmask', 'bond_type', 'manage_vlan', 'manage_nic1', 'manage_nic2',
            'ipmi_address', 'ipmi_user', 'ipmi_password', 'ipmi_vlan',
            'storage_vlan', 'storage_ifname', 'storage_address', 'storage_netmask',
            'business_vlan', 'business_ifname', 'business_address', 'business_netmask',
            'raid', 'asset_number', 'server_brand', 'server_model',
            'base_location', 'server_room_number', 'cabinet_number',
            'cluster_name', 'region'
        ]


class HostUpdateSerializer(serializers.ModelSerializer):
    """主机更新序列化器"""
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Host
        fields = [
            'serial_number', 'hostname', 'port', 'username', 'password',
            'cluster', 'status', 'os_type', 'host_type',
            'use_name', 'use_for',
            'netmask', 'bond_type', 'manage_vlan', 'manage_nic1', 'manage_nic2',
            'manage_address_ipv6', 'manage_netmask_ipv6',
            'ipmi_address', 'ipmi_user', 'ipmi_password', 'ipmi_vlan',
            'storage_vlan', 'storage_ifname', 'storage_address', 'storage_netmask',
            'business_vlan', 'business_ifname', 'business_address', 'business_netmask',
            'business_bond_type', 'business_nic1', 'business_nic2',
            'other_vlan', 'other_ifname', 'other_address', 'other_netmask',
            'other_nic1', 'other_nic2',
            'is_cluster_type', 'is_zone_type', 'is_bind_cell_type', 'flag',
            'raid', 'bios_config', 'asset_number', 'is_warranty_period',
            'server_brand', 'server_model', 'server_size',
            'base_location', 'server_room_number', 'cabinet_number',
            'cluster_name', 'cell_vip', 'ntp_address',
            'arch_info', 'os_version', 'uptime', 'cpu_info', 'disk_info',
            'memory_info', 'network_info', 'mount_info', 'dmesg_info',
            'mac_address', 'region', 'lldp_infos'
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = password
        instance.save()
        return instance


class HostListSerializer(serializers.ModelSerializer):
    """主机列表序列化器（简化字段）"""
    cluster_name = serializers.CharField(source='cluster.name', read_only=True)

    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'ip_address', 'port', 'cluster', 'cluster_name',
            'status', 'os_type', 'host_type', 'serial_number'
        ]


class VMSerializer(serializers.ModelSerializer):
    """VM序列化器（完整信息）"""
    host_name = serializers.CharField(source='host.hostname', read_only=True, allow_null=True)
    cluster_name = serializers.CharField(source='cluster.name', read_only=True, allow_null=True)

    class Meta:
        model = VM
        fields = [
            'id', 'name', 'uuid', 'mac_address',
            'host', 'host_name', 'cluster', 'cluster_name',
            'status', 'vcpu', 'memory', 'disk',
            'ip_address', 'management_ip', 'storage_ip',
            'os_type',
            'vm_image_path', 'vm_disk_path', 'vm_network_bridge',
            'imageid', 'sysdisk', 'datadisk', 'status_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VMCreateSerializer(serializers.ModelSerializer):
    """VM创建序列化器"""
    class Meta:
        model = VM
        fields = [
            'name', 'uuid', 'mac_address', 'host', 'cluster',
            'status', 'vcpu', 'memory', 'disk',
            'ip_address', 'management_ip', 'storage_ip',
            'os_type', 'vm_image_path', 'vm_disk_path', 'vm_network_bridge',
            'imageid', 'sysdisk', 'datadisk'
        ]


class VMUpdateSerializer(serializers.ModelSerializer):
    """VM更新序列化器"""
    class Meta:
        model = VM
        fields = [
            'name', 'mac_address', 'host', 'cluster',
            'status', 'vcpu', 'memory', 'disk',
            'ip_address', 'management_ip', 'storage_ip',
            'os_type', 'vm_image_path', 'vm_disk_path', 'vm_network_bridge',
            'imageid', 'sysdisk', 'datadisk', 'status_message'
        ]


class VMListSerializer(serializers.ModelSerializer):
    """VM列表序列化器（简化字段）"""
    host_name = serializers.CharField(source='host.hostname', read_only=True)
    cluster_name = serializers.CharField(source='cluster.name', read_only=True)

    class Meta:
        model = VM
        fields = [
            'id', 'name', 'uuid', 'host', 'host_name', 'cluster', 'cluster_name',
            'status', 'vcpu', 'ip_address', 'os_type'
        ]


class ImageSerializer(serializers.ModelSerializer):
    """镜像序列化器"""
    host_name = serializers.CharField(source='host.hostname', read_only=True, allow_null=True)

    class Meta:
        model = Image
        fields = ['id', 'name', 'ostype', 'path', 'host', 'host_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ImageCreateSerializer(serializers.ModelSerializer):
    """镜像创建序列化器"""
    class Meta:
        model = Image
        fields = ['id', 'name', 'ostype', 'path', 'host']


class ImageUpdateSerializer(serializers.ModelSerializer):
    """镜像更新序列化器"""
    class Meta:
        model = Image
        fields = ['name', 'ostype', 'path', 'host']