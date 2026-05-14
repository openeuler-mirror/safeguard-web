"""KickStartFileStatus 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.osdeploy import KickStartFileStatus, RepoStatus


class KickStartViewSetTest(APITestCase):
    """KickStartViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_ks',
            password='testpass123',
            nickname='测试用户'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.repo = RepoStatus.objects.create(
            name='test-repo',
            repo_type='yum',
            base_url='http://repo.example.com'
        )

    def test_list_kickstarts(self):
        """测试列出Kickstart模板"""
        KickStartFileStatus.objects.create(
            name='ks-1',
            content='#!ks',
            repo=self.repo
        )
        KickStartFileStatus.objects.create(
            name='ks-2',
            content='#!ks',
            repo=self.repo
        )
        response = self.client.get('/api/kickstarts/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_kickstart(self):
        """测试创建Kickstart模板"""
        data = {
            'name': 'new-kickstart',
            'content': '#!ks\ngraphical',
            'repo': self.repo.pk,
            'kernel_options': {'net.ifnames': '0'},
            'description': '新模板'
        }
        response = self.client.post('/api/kickstarts/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'new-kickstart')

    def test_retrieve_kickstart(self):
        """测试获取单个Kickstart模板"""
        ks = KickStartFileStatus.objects.create(
            name='test-ks',
            content='#!ks',
            repo=self.repo
        )
        response = self.client.get(f'/api/kickstarts/{ks.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'test-ks')
        self.assertEqual(response.data['data']['repo_name'], 'test-repo')

    def test_update_kickstart(self):
        """测试更新Kickstart模板"""
        ks = KickStartFileStatus.objects.create(
            name='original-ks',
            content='#!ks',
            repo=self.repo
        )
        data = {
            'name': 'updated-ks',
            'content': '#!ks\nupdated',
            'repo': self.repo.pk,
            'kernel_options': {'quiet': True},
            'description': '更新后的模板'
        }
        response = self.client.put(f'/api/kickstarts/{ks.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'updated-ks')

    def test_partial_update_kickstart(self):
        """测试部分更新Kickstart模板"""
        ks = KickStartFileStatus.objects.create(
            name='partial-ks',
            content='#!ks',
            repo=self.repo
        )
        data = {'description': '新描述'}
        response = self.client.patch(f'/api/kickstarts/{ks.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['description'], '新描述')

    def test_delete_kickstart(self):
        """测试删除Kickstart模板"""
        ks = KickStartFileStatus.objects.create(
            name='to-delete-ks',
            content='#!ks',
            repo=self.repo
        )
        response = self.client.delete(f'/api/kickstarts/{ks.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(KickStartFileStatus.objects.filter(pk=ks.pk).exists())

    def test_validate_kickstart_action(self):
        """测试验证Kickstart模板action"""
        ks = KickStartFileStatus.objects.create(
            name='validate-ks',
            content='#!ks',
            repo=self.repo
        )
        response = self.client.post(f'/api/kickstarts/{ks.pk}/validate/')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('验证', response.data['errmsg'])

    def test_preview_kickstart_action(self):
        """测试预览Kickstart模板action"""
        ks = KickStartFileStatus.objects.create(
            name='preview-ks',
            content='network --bootp={{{BOOTP_SERVER}}}\nrootpw={{{ROOT_PASSWORD}}}',
            repo=self.repo
        )
        vars = {'BOOTP_SERVER': '192.168.1.1', 'ROOT_PASSWORD': 'secret'}
        response = self.client.post(f'/api/kickstarts/{ks.pk}/preview/', {'vars': vars}, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('192.168.1.1', response.data['data']['content'])
        self.assertIn('secret', response.data['data']['content'])