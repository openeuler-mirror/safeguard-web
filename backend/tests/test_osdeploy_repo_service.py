"""RepoService 测试"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from backend.models.osdeploy import RepoStatus
from backend.services.osdeploy import RepoService


class RepoServiceTest(TestCase):
    """RepoService 测试"""

    def setUp(self):
        self.repo = RepoStatus.objects.create(
            name='TestRepo',
            repo_type='yum',
            base_url='http://example.com/repo',
            is_default=True
        )

    def test_list_repos(self):
        """测试获取仓库列表"""
        result = RepoService.list_repos()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'TestRepo')

    def test_list_repos_with_pagination(self):
        """测试仓库列表分页"""
        for i in range(15):
            RepoStatus.objects.create(
                name=f'PaginatedRepo{i}',
                repo_type='http',
                base_url=f'http://example.com/repo{i}'
            )
        result = RepoService.list_repos(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_repos_with_filter(self):
        """测试仓库列表过滤"""
        RepoStatus.objects.create(
            name='FilterRepo',
            repo_type='iso',
            base_url='http://example.com/iso'
        )
        result = RepoService.list_repos(filters={'repo_type': 'iso'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'FilterRepo')

    def test_get_repo(self):
        """测试获取仓库详情"""
        repo = RepoService.get_repo(self.repo.id)
        self.assertIsNotNone(repo)
        self.assertEqual(repo.name, 'TestRepo')

    def test_get_repo_not_found(self):
        """测试获取不存在的仓库"""
        repo = RepoService.get_repo(9999)
        self.assertIsNone(repo)

    def test_create_repo(self):
        """测试创建仓库"""
        data = {
            'name': 'NewRepo',
            'repo_type': 'http',
            'base_url': 'http://example.com/new',
            'is_default': False
        }
        repo = RepoService.create_repo(data)
        self.assertEqual(repo.name, 'NewRepo')
        self.assertEqual(repo.repo_type, 'http')

    def test_create_repo_set_default(self):
        """测试创建仓库并设为默认"""
        data = {
            'name': 'DefaultRepo',
            'repo_type': 'yum',
            'base_url': 'http://example.com/default',
            'is_default': True
        }
        repo = RepoService.create_repo(data)
        self.assertTrue(repo.is_default)
        # 验证之前的默认仓库被取消
        self.repo.refresh_from_db()
        self.assertFalse(self.repo.is_default)

    def test_update_repo(self):
        """测试更新仓库"""
        data = {'name': 'UpdatedRepo', 'description': '更新描述'}
        repo = RepoService.update_repo(self.repo.id, data)
        self.assertEqual(repo.name, 'UpdatedRepo')
        self.assertEqual(repo.description, '更新描述')

    def test_update_repo_not_found(self):
        """测试更新不存在的仓库"""
        result = RepoService.update_repo(9999, {'name': 'Test'})
        self.assertIsNone(result)

    def test_delete_repo(self):
        """测试删除仓库"""
        result = RepoService.delete_repo(self.repo.id)
        self.assertTrue(result)
        self.assertFalse(RepoStatus.objects.filter(id=self.repo.id).exists())

    def test_delete_repo_not_found(self):
        """测试删除不存在的仓库"""
        result = RepoService.delete_repo(9999)
        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_sync_repo(self, mock_urlopen):
        """测试同步仓库"""
        mock_urlopen.return_value = MagicMock()
        result = RepoService.sync_repo(self.repo.id)
        self.assertEqual(result['repo_id'], self.repo.id)
        self.assertEqual(result['repo_name'], 'TestRepo')
        self.assertEqual(result['status'], 'synced')
        self.assertIn('job_id', result)
        self.assertIsNotNone(result['job_id'])

        from backend.models.task import Task
        task = Task.objects.get(job_id=result['job_id'])
        self.assertEqual(task.job_type, 'repo_sync')
        self.assertEqual(task.target, 'TestRepo')

    def test_sync_repo_iso(self):
        """测试同步 ISO 仓库"""
        repo = RepoStatus.objects.create(
            name='IsoRepo',
            repo_type='iso',
            base_url='/nonexistent/iso.iso'
        )
        result = RepoService.sync_repo(repo.id)
        self.assertEqual(result['repo_id'], repo.id)
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(len(result['errors']) > 0)

    def test_sync_repo_not_found(self):
        """测试同步不存在的仓库"""
        with self.assertRaises(ValueError):
            RepoService.sync_repo(9999)

    def test_get_default_repo(self):
        """测试获取默认仓库"""
        repo = RepoService.get_default_repo()
        self.assertIsNotNone(repo)
        self.assertEqual(repo.name, 'TestRepo')

    def test_get_default_repo_not_found(self):
        """测试没有默认仓库"""
        self.repo.is_default = False
        self.repo.save()
        repo = RepoService.get_default_repo()
        self.assertIsNone(repo)
