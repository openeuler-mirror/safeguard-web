from django.test import TestCase

from backend.models.osdeploy.kickstart_file_status import KickStartFileStatus
from backend.models.osdeploy.repo_status import RepoStatus


class KickStartFileStatusModelTest(TestCase):
    """KickStartFileStatus 模型测试"""

    def setUp(self):
        self.repo = RepoStatus.objects.create(
            name='CentOS-7-repo',
            repo_type='yum',
            base_url='http://mirror.example.com/centos/7/'
        )

    def test_create_kickstart_file_status(self):
        """测试创建Kickstart文件状态"""
        ks = KickStartFileStatus.objects.create(
            name='centos7-standard',
            content='url --url="http://example.com/centos7"\nkeyboard us\nlang en_US',
            repo=self.repo
        )
        self.assertEqual(ks.name, 'centos7-standard')
        self.assertIn('url --url', ks.content)
        self.assertEqual(ks.repo, self.repo)

    def test_kickstart_file_status_str(self):
        """测试Kickstart文件状态字符串表示"""
        ks = KickStartFileStatus(name='MyKickstart')
        self.assertEqual(str(ks), 'MyKickstart')

    def test_kickstart_name_unique(self):
        """测试Kickstart名称唯一性"""
        KickStartFileStatus.objects.create(
            name='UniqueKS',
            content='content1',
            repo=self.repo
        )
        with self.assertRaises(Exception):
            KickStartFileStatus.objects.create(
                name='UniqueKS',
                content='content2',
                repo=self.repo
            )

    def test_kickstart_default_values(self):
        """测试Kickstart默认值"""
        ks = KickStartFileStatus.objects.create(
            name='DefaultKS',
            content='default content'
        )
        self.assertEqual(ks.repo, None)
        self.assertEqual(ks.kernel_options, {})
        self.assertEqual(ks.description, '')

    def test_kickstart_with_kernel_options(self):
        """测试Kickstart内核参数"""
        ks = KickStartFileStatus.objects.create(
            name='ks-with-options',
            content='content',
            kernel_options={
                'ksdevice': 'eth0',
                'ip': '192.168.1.100',
                'netmask': '255.255.255.0',
                'gateway': '192.168.1.1'
            }
        )
        self.assertEqual(ks.kernel_options['ksdevice'], 'eth0')
        self.assertEqual(ks.kernel_options['ip'], '192.168.1.100')

    def test_kickstart_with_description(self):
        """测试Kickstart描述"""
        ks = KickStartFileStatus.objects.create(
            name='DescribedKS',
            content='content',
            description='Standard kickstart for CentOS 7'
        )
        self.assertEqual(ks.description, 'Standard kickstart for CentOS 7')

    def test_kickstart_repo_relation(self):
        """测试Kickstart与仓库的关联"""
        ks1 = KickStartFileStatus.objects.create(
            name='ks-repo1',
            content='content1',
            repo=self.repo
        )
        ks2 = KickStartFileStatus.objects.create(
            name='ks-repo2',
            content='content2',
            repo=self.repo
        )
        self.assertEqual(self.repo.kickstartfilestatus_set.count(), 2)
        self.assertIn(ks1, self.repo.kickstartfilestatus_set.all())
        self.assertIn(ks2, self.repo.kickstartfilestatus_set.all())

    def test_kickstart_without_repo(self):
        """测试无仓库关联的Kickstart"""
        ks = KickStartFileStatus.objects.create(
            name='ks-no-repo',
            content='content without repo'
        )
        self.assertIsNone(ks.repo)

    def test_kickstart_ordering(self):
        """测试Kickstart按ID顺序排列"""
        ks1 = KickStartFileStatus.objects.create(
            name='order-ks1',
            content='content1'
        )
        ks2 = KickStartFileStatus.objects.create(
            name='order-ks2',
            content='content2'
        )
        kss = KickStartFileStatus.objects.all()
        self.assertEqual(kss[0], ks1)
        self.assertEqual(kss[1], ks2)