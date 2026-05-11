from django.test import TestCase

from backend.models.osdeploy.repo_status import RepoStatus


class RepoStatusModelTest(TestCase):
    """RepoStatus 模型测试"""

    def test_create_repo_status(self):
        """测试创建仓库状态"""
        repo = RepoStatus.objects.create(
            name='CentOS-7-repo',
            repo_type='yum',
            base_url='http://mirror.example.com/centos/7/'
        )
        self.assertEqual(repo.name, 'CentOS-7-repo')
        self.assertEqual(repo.repo_type, 'yum')
        self.assertEqual(repo.base_url, 'http://mirror.example.com/centos/7/')

    def test_repo_status_str(self):
        """测试仓库状态字符串表示"""
        repo = RepoStatus(name='MyRepo')
        self.assertEqual(str(repo), 'MyRepo')

    def test_repo_name_unique(self):
        """测试仓库名称唯一性"""
        RepoStatus.objects.create(
            name='UniqueRepo',
            repo_type='yum',
            base_url='http://example.com/repo'
        )
        with self.assertRaises(Exception):
            RepoStatus.objects.create(
                name='UniqueRepo',
                repo_type='http',
                base_url='http://example.com/repo2'
            )

    def test_repo_status_default_values(self):
        """测试仓库状态默认值"""
        repo = RepoStatus.objects.create(
            name='DefaultRepo',
            repo_type='yum',
            base_url='http://example.com/default'
        )
        self.assertFalse(repo.is_default)
        self.assertEqual(repo.description, '')

    def test_repo_status_all_repo_type_choices(self):
        """测试仓库类型所有选项"""
        for repo_type_value, repo_type_label in RepoStatus.REPO_TYPE_CHOICES:
            repo = RepoStatus.objects.create(
                name=f'repo-{repo_type_value}',
                repo_type=repo_type_value,
                base_url=f'http://example.com/{repo_type_value}'
            )
            self.assertEqual(repo.repo_type, repo_type_value)

    def test_repo_status_is_default(self):
        """测试仓库默认标识"""
        repo1 = RepoStatus.objects.create(
            name='Repo-Default-1',
            repo_type='yum',
            base_url='http://example.com/repo1',
            is_default=True
        )
        repo2 = RepoStatus.objects.create(
            name='Repo-Default-2',
            repo_type='http',
            base_url='http://example.com/repo2',
            is_default=False
        )
        self.assertTrue(repo1.is_default)
        self.assertFalse(repo2.is_default)

    def test_repo_status_with_description(self):
        """测试仓库描述"""
        repo = RepoStatus.objects.create(
            name='DescribedRepo',
            repo_type='iso',
            base_url='http://example.com/iso',
            description='This is a test repository for OS deployment'
        )
        self.assertEqual(repo.description, 'This is a test repository for OS deployment')

    def test_repo_status_ordering(self):
        """测试仓库按ID顺序排列"""
        repo1 = RepoStatus.objects.create(
            name='OrderRepo1',
            repo_type='yum',
            base_url='http://example.com/order1'
        )
        repo2 = RepoStatus.objects.create(
            name='OrderRepo2',
            repo_type='http',
            base_url='http://example.com/order2'
        )
        repos = RepoStatus.objects.all()
        self.assertEqual(repos[0], repo1)
        self.assertEqual(repos[1], repo2)