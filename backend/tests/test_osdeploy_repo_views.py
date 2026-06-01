"""RepoStatus 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.osdeploy import RepoStatus, KickStartFileStatus


class RepoViewSetTest(APITestCase):
    """RepoViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_repo',
            password='testpass123',
            nickname='测试用户'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_repos(self):
        """测试列出仓库"""
        RepoStatus.objects.create(
            name='repo-1',
            repo_type='yum',
            base_url='http://repo.example.com/yum'
        )
        RepoStatus.objects.create(
            name='repo-2',
            repo_type='iso',
            base_url='http://repo.example.com/iso'
        )
        response = self.client.get('/api/repos/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_repo(self):
        """测试创建仓库"""
        data = {
            'name': 'new-repo',
            'repo_type': 'yum',
            'base_url': 'http://newrepo.example.com/yum',
            'is_default': False,
            'description': '新仓库'
        }
        response = self.client.post('/api/repos/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'new-repo')

    def test_retrieve_repo(self):
        """测试获取单个仓库"""
        repo = RepoStatus.objects.create(
            name='test-repo',
            repo_type='http',
            base_url='http://test.example.com'
        )
        response = self.client.get(f'/api/repos/{repo.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'test-repo')

    def test_update_repo(self):
        """测试更新仓库"""
        repo = RepoStatus.objects.create(
            name='original-repo',
            repo_type='yum',
            base_url='http://original.example.com'
        )
        data = {
            'name': 'updated-repo',
            'repo_type': 'iso',
            'base_url': 'http://updated.example.com',
            'is_default': True,
            'description': '更新后的描述'
        }
        response = self.client.put(f'/api/repos/{repo.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'updated-repo')
        self.assertEqual(response.data['data']['repo_type'], 'iso')

    def test_partial_update_repo(self):
        """测试部分更新仓库"""
        repo = RepoStatus.objects.create(
            name='partial-repo',
            repo_type='yum',
            base_url='http://partial.example.com'
        )
        data = {'description': '新描述'}
        response = self.client.patch(f'/api/repos/{repo.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['description'], '新描述')

    def test_delete_repo(self):
        """测试删除仓库"""
        repo = RepoStatus.objects.create(
            name='to-delete-repo',
            repo_type='yum',
            base_url='http://delete.example.com'
        )
        response = self.client.delete(f'/api/repos/{repo.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(RepoStatus.objects.filter(pk=repo.pk).exists())

    def test_delete_repo_with_kickstart_fails(self):
        """测试删除有关联Kickstart的仓库失败"""
        repo = RepoStatus.objects.create(
            name='repo-with-kickstart',
            repo_type='yum',
            base_url='http://kickstart.example.com'
        )
        KickStartFileStatus.objects.create(
            name='kickstart-1',
            content='#test',
            repo=repo
        )
        response = self.client.delete(f'/api/repos/{repo.pk}/')
        self.assertNotEqual(response.data['errno'], 0)
        self.assertIn('Kickstart', response.data['errmsg'])

    def test_sync_repo_action(self):
        """测试同步仓库action"""
        repo = RepoStatus.objects.create(
            name='sync-test-repo',
            repo_type='yum',
            base_url='http://sync.example.com'
        )
        response = self.client.post(f'/api/repos/{repo.pk}/sync/')
        self.assertEqual(response.data['errno'], 0)
        data = response.data['data']
        self.assertEqual(data['repo_id'], repo.pk)
        self.assertEqual(data['status'], 'synced')