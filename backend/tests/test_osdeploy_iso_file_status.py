from django.test import TestCase

from backend.models.osdeploy.iso_file_status import ISOFileStatus


class ISOFileStatusModelTest(TestCase):
    """ISOFileStatus 模型测试"""

    def test_create_iso_file_status(self):
        """测试创建ISO文件状态"""
        iso = ISOFileStatus.objects.create(
            filename='CentOS-7-x86_64-DVD-2009.iso',
            size=4367050752,  # ~4.1GB
            md5sum='a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4'
        )
        self.assertEqual(iso.filename, 'CentOS-7-x86_64-DVD-2009.iso')
        self.assertEqual(iso.size, 4367050752)
        self.assertEqual(iso.md5sum, 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4')

    def test_iso_file_status_str(self):
        """测试ISO文件状态字符串表示"""
        iso = ISOFileStatus(filename='ubuntu-22.04.iso')
        self.assertEqual(str(iso), 'ubuntu-22.04.iso')

    def test_iso_filename_unique(self):
        """测试ISO文件名唯一性"""
        ISOFileStatus.objects.create(
            filename='unique-file.iso',
            size=1000000,
            md5sum='aaa'
        )
        with self.assertRaises(Exception):
            ISOFileStatus.objects.create(
                filename='unique-file.iso',
                size=2000000,
                md5sum='bbb'
            )

    def test_iso_default_values(self):
        """测试ISO文件状态默认值"""
        iso = ISOFileStatus.objects.create(
            filename='default.iso',
            size=1000000,
            md5sum='md5sum123'
        )
        self.assertEqual(iso.status, 'available')
        self.assertEqual(iso.file_path, '')
        self.assertEqual(iso.description, '')

    def test_iso_all_status_choices(self):
        """测试ISO文件所有状态选项"""
        for status_value, status_label in ISOFileStatus.STATUS_CHOICES:
            iso = ISOFileStatus.objects.create(
                filename=f'iso-{status_value}.iso',
                size=1000000,
                md5sum=f'md5-{status_value}',
                status=status_value
            )
            self.assertEqual(iso.status, status_value)

    def test_iso_with_file_path(self):
        """测试ISO文件路径"""
        iso = ISOFileStatus.objects.create(
            filename='path-test.iso',
            size=1000000,
            md5sum='md5',
            file_path='/data/isos/centos/7/'
        )
        self.assertEqual(iso.file_path, '/data/isos/centos/7/')

    def test_iso_with_description(self):
        """测试ISO文件描述"""
        iso = ISOFileStatus.objects.create(
            filename='described.iso',
            size=1000000,
            md5sum='md5',
            description='CentOS 7.9 DVD ISO'
        )
        self.assertEqual(iso.description, 'CentOS 7.9 DVD ISO')

    def test_iso_ordering(self):
        """测试ISO文件按ID顺序排列"""
        iso1 = ISOFileStatus.objects.create(
            filename='order1.iso',
            size=1000000,
            md5sum='md51'
        )
        iso2 = ISOFileStatus.objects.create(
            filename='order2.iso',
            size=2000000,
            md5sum='md52'
        )
        isos = ISOFileStatus.objects.all()
        self.assertEqual(isos[0], iso1)
        self.assertEqual(isos[1], iso2)