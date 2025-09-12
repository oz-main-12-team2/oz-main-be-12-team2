from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


class UserModelTest(TestCase):
    """User 모델 테스트"""

    def test_create_user(self):
        """일반 사용자 생성 테스트"""
        user = User.objects.create_user(
            email='test@example.com',
            name='테스트 사용자',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, '테스트 사용자')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_social)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        """슈퍼유저 생성 테스트"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            name='관리자',
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_social)

    def test_create_social_user(self):
        """소셜 사용자 생성 테스트"""
        user = User.objects.create_user(
            email='social@example.com',
            name='소셜 사용자',
            is_social=True
        )
        self.assertEqual(user.email, 'social@example.com')
        self.assertTrue(user.is_social)
        self.assertIsNone(user.password)


class UserAPITest(TestCase):
    """User API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user_register')
        self.login_url = reverse('user_login')

    def test_user_registration(self):
        """회원가입 API 테스트"""
        data = {
            'email': 'newuser@example.com',
            'name': '신규 사용자',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'address': '서울시 강남구'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertEqual(response.data['name'], '신규 사용자')

        # 비밀번호는 응답에 포함되지 않아야 함
        self.assertNotIn('password', response.data)

    def test_user_registration_password_mismatch(self):
        """비밀번호 불일치 테스트"""
        data = {
            'email': 'newuser@example.com',
            'name': '신규 사용자',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_user_login(self):
        """로그인 API 테스트"""
        # 먼저 사용자 생성
        user = User.objects.create_user(
            email='logintest@example.com',
            name='로그인 테스트',
            password='loginpass123'
        )

        # 로그인 시도
        data = {
            'email': 'logintest@example.com',
            'password': 'loginpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """잘못된 로그인 정보 테스트"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class AdminAPITest(TestCase):
    """관리자 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            name='관리자',
            password='adminpass123',
            is_admin=True
        )
        # 일반 사용자 생성
        self.normal_user = User.objects.create_user(
            email='user@example.com',
            name='일반 사용자',
            password='userpass123'
        )

    def test_admin_user_list_with_admin(self):
        """관리자 권한으로 사용자 목록 조회"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_user_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 관리자 + 일반 사용자

    def test_admin_user_list_with_normal_user(self):
        """일반 사용자가 관리자 API 접근 시도"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('admin_user_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ChangePasswordTest(TestCase):
    """비밀번호 변경 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            name='테스트 사용자',
            password='oldpassword123'
        )
        self.social_user = User.objects.create_user(
            email='social@example.com',
            name='소셜 사용자',
            is_social=True
        )
        self.change_password_url = '/api/user/change-password/'

    def test_change_password_success(self):
        """비밀번호 변경 성공 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # 새 비밀번호로 로그인 확인
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

    def test_change_password_wrong_old_password(self):
        """잘못된 기존 비밀번호 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

        # 기존 비밀번호 그대로 유지 확인
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpassword123'))

    def test_change_password_mismatch(self):
        """새 비밀번호 불일치 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'new_password_confirm': 'differentpassword'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password_confirm', response.data)

    def test_change_password_weak_password(self):
        """약한 비밀번호 테스트 (Django validation)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': '123',  # 너무 짧은 비밀번호
            'new_password_confirm': '123'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_change_password_social_user(self):
        """소셜 사용자 비밀번호 변경 시도 테스트"""
        self.client.force_authenticate(user=self.social_user)
        data = {
            'old_password': 'anypassword',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('소셜 로그인 사용자', response.data['error'])

    def test_change_password_unauthenticated(self):
        """인증되지 않은 사용자 테스트"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_missing_fields(self):
        """필수 필드 누락 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            # new_password 누락
            'new_password_confirm': 'newpassword456'
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)