from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class UserModelTest(TestCase):
    """User 모델 테스트"""

    def test_create_user(self):
        """일반 사용자 생성 테스트"""
        user = User.objects.create_user(email="test@example.com", name="테스트 사용자", password="testpass123")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "테스트 사용자")
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_social)
        self.assertTrue(user.check_password("testpass123"))

    def test_create_superuser(self):
        """슈퍼유저 생성 테스트"""
        user = User.objects.create_superuser(email="admin@example.com", name="관리자", password="adminpass123")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_social)

    def test_create_social_user(self):
        """소셜 사용자 생성 테스트"""
        user = User.objects.create_user(email="social@example.com", name="소셜 사용자", is_social=True)
        self.assertEqual(user.email, "social@example.com")
        self.assertTrue(user.is_social)
        self.assertIsNone(user.password)

    def test_create_user_without_email(self):
        """이메일 없이 사용자 생성 시 ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email="", name="테스트 사용자", password="password123")
        self.assertEqual(str(context.exception), "이메일은 필수입니다.")

    def test_create_user_without_name(self):
        """이름 없이 사용자 생성 시 ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email="test@example.com", name="", password="password123")
        self.assertEqual(str(context.exception), "이름은 필수입니다.")

    def test_create_user_without_password_for_normal_user(self):
        """일반 사용자인데 비밀번호 없이 생성 시 ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email="test@example.com", name="테스트 사용자", password=None)
        self.assertEqual(str(context.exception), "일반 회원가입 시 비밀번호는 필수입니다.")

    def test_create_social_user_without_password(self):
        """소셜 사용자는 비밀번호 없이 생성 가능"""
        user = User.objects.create_user(email="social@example.com", name="소셜 사용자", password=None, is_social=True)
        self.assertEqual(user.email, "social@example.com")
        self.assertTrue(user.is_social)
        self.assertIsNone(user.password)

    def test_create_superuser_without_email(self):
        """슈퍼유저 생성 시 이메일 없으면 ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(email="superuser@example.com", name="슈퍼유저", password=None)
        self.assertEqual(str(context.exception), "슈퍼유저는 비밀번호가 필수입니다.")

    # UserModelTest 클래스에 추가할 메서드들

    def test_user_str_method(self):
        """User 모델의 __str__ 메서드 테스트"""
        user = User.objects.create_user(email="str_test@example.com", name="문자열 테스트", password="password123")
        self.assertEqual(str(user), "str_test@example.com")

    def test_is_staff_property(self):
        """is_staff 프로퍼티 테스트"""
        # 일반 사용자
        normal_user = User.objects.create_user(email="normal@example.com", name="일반 사용자", password="password123")
        self.assertFalse(normal_user.is_staff)

        # 관리자 사용자
        admin_user = User.objects.create_user(
            email="admin@example.com", name="관리자", password="password123", is_admin=True
        )
        self.assertTrue(admin_user.is_staff)

    def test_save_method_social_user_password_none(self):
        """소셜 사용자 저장 시 password가 None으로 설정되는지 테스트"""
        user = User.objects.create_user(
            email="social@example.com",
            name="소셜 사용자",
            password="temporary_password",  # 임시 패스워드 설정
            is_social=True,
        )
        # save() 메서드에서 소셜 사용자는 password가 None으로 설정됨
        self.assertIsNone(user.password)

    def test_save_method_normal_user_without_password_new_user(self):
        """신규 일반 사용자 생성 시 비밀번호 없으면 ValidationError"""
        user = User(email="test@example.com", name="테스트 사용자")  # password 없음

        with self.assertRaises(ValidationError) as context:
            user.save()
        self.assertEqual(str(context.exception), "['일반 회원가입 시 비밀번호는 필수입니다.']")

    def test_clean_method_normal_user_without_password(self):
        """clean 메서드에서 일반 사용자 비밀번호 검증"""
        user = User(email="test@example.com", name="테스트 사용자")  # password 없음

        with self.assertRaises(ValidationError) as context:
            user.clean()
        self.assertEqual(context.exception.message_dict["password"][0], "일반 회원가입 시 비밀번호는 필수입니다.")

    def test_clean_method_social_user_without_password(self):
        """소셜 사용자는 비밀번호 없어도 clean 통과"""
        user = User(email="social@example.com", name="소셜 사용자", is_social=True)
        # clean 호출 시 예외가 발생하지 않아야 함
        try:
            user.clean()
        except ValidationError:
            self.fail("소셜 사용자는 비밀번호 없어도 clean을 통과해야 합니다.")


class UserAPITest(TestCase):
    """User API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("user_register")
        self.login_url = reverse("user_login")
        self.logout_url = reverse("user_logout")

    def test_user_registration(self):
        """회원가입 API 테스트"""
        data = {
            "email": "newuser@example.com",
            "name": "신규 사용자",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "address": "서울시 강남구",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 비밀번호는 응답에 포함되지 않아야 함
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["message"], "인증 메일이 발송되었습니다.")

    def test_user_registration_password_mismatch(self):
        """비밀번호 불일치 테스트"""
        data = {
            "email": "newuser@example.com",
            "name": "신규 사용자",
            "password": "newpass123",
            "password_confirm": "differentpass",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_user_login_missing_credentials(self):
        """필수 정보 누락 시 에러"""
        data = {}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일과 비밀번호를 입력해주세요.")

    def test_user_login_invalid_credentials(self):
        """잘못된 로그인 정보 테스트"""
        data = {"email": "nonexistent@example.com", "password": "wrongpass"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.data["error"], "이메일 또는 비밀번호가 올바르지 않습니다.")
        self.assertIn("error", response.data)

    def test_user_login_inactive_user(self):
        """비활성화된 계정으로 로그인 시도 (Django 기본설정상 체크불가능)"""
        User.objects.create_user(
            email="inactive@example.com", name="비활성 사용자", password="password123", is_active=False
        )

        data = {"email": "inactive@example.com", "password": "password123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일 또는 비밀번호가 올바르지 않습니다.")

    def test_logout_without_refresh_token(self):
        """refresh_token 없이 호출"""
        # 사용자 생성 및 인증 설정
        user = User.objects.create_user(
            email="logouttest@example.com",
            name="로그아웃 테스트",
            password="logoutpass123",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, 200)

    def test_user_profile_get(self):
        """사용자 프로필 조회 테스트"""
        user = User.objects.create_user(email="profile@example.com", name="프로필 테스트", password="profilepass123")
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_put_success(self):
        """사용자 프로필 수정 성공 테스트"""
        user = User.objects.create_user(email="profile@example.com", name="프로필 테스트", password="profilepass123")
        self.client.force_authenticate(user=user)

        data = {"name": "수정된 이름"}
        response = self.client.put(reverse("user_profile"), data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_user_profile_put_invalid_data(self):
        """사용자 프로필 수정 실패 테스트"""
        user = User.objects.create_user(email="profile@example.com", name="프로필 테스트", password="profilepass123")
        self.client.force_authenticate(user=user)

        data = {"name": ""}  # 잘못된 이름 형식
        response = self.client.put(reverse("user_profile"), data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_user_delete(self):
        """회원 탈퇴 테스트"""
        user = User.objects.create_user(email="delete@example.com", name="탈퇴 테스트", password="deletepass123")
        self.client.force_authenticate(user=user)

        response = self.client.delete(reverse("user_delete"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "회원탈퇴가 완료되었습니다.")

        # 사용자가 실제로 삭제되었는지 확인
        self.assertFalse(User.objects.filter(email="delete@example.com").exists())

    def test_activate_user_success(self):
        """정상적인 활성화"""
        user = User.objects.create_user(
            email="test@example.com", name="활성화 테스트", password="testpass123", is_active=False
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(reverse("user_activate", kwargs={"uidb64": uid, "token": token}))
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_activate_user_invalid_uid(self):
        """잘못된 UID"""
        user = User.objects.create_user(email="test@example.com", name="잘못된 활성화 테스트", password="testpass123")
        token = default_token_generator.make_token(user)

        response = self.client.get(reverse("user_activate", kwargs={"uidb64": "invalid_uid", "token": token}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "잘못된 링크입니다.")

    def test_activate_user_nonexistent_user(self):
        """존재하지 않는 사용자 ID"""
        fake_uid = urlsafe_base64_encode(force_bytes(99999))
        response = self.client.get(reverse("user_activate", kwargs={"uidb64": fake_uid, "token": "fake_token"}))
        self.assertEqual(response.status_code, 400)

    def test_activate_user_invalid_token(self):
        """잘못된 토큰"""
        user = User.objects.create_user(email="test@example.com", name="토큰 테스트", password="testpass123")
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(reverse("user_activate", kwargs={"uidb64": uid, "token": "invalid_token"}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "유효하지 않은 토큰입니다.")

    def test_password_reset_request_success(self):
        """비밀번호 재설정 요청 성공"""
        User.objects.create_user(email="reset@example.com", name="재설정 테스트", password="testpass123")

        data = {"email": "reset@example.com"}
        response = self.client.post(reverse("password_reset_request"), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "비밀번호 재설정 메일이 발송되었습니다.")

    def test_password_reset_request_user_not_found(self):
        """존재하지 않는 이메일로 재설정 요청"""
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(reverse("password_reset_request"), data, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "해당 이메일의 사용자가 없습니다.")

    def test_password_reset_request_invalid_data(self):
        """잘못된 데이터로 재설정 요청"""
        data = {"email": "invalid-email"}  # 잘못된 이메일 형식
        response = self.client.post(reverse("password_reset_request"), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_password_reset_request_missing_email(self):
        """이메일 누락"""
        data = {}
        response = self.client.post(reverse("password_reset_request"), data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_success(self):
        """비밀번호 재설정 확인 성공"""
        user = User.objects.create_user(
            email="resetconfirm@example.com", name="재설정확인 테스트", password="oldpass123"
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        data = {"new_password": "newpass123", "new_password_confirm": "newpass123"}
        response = self.client.post(
            reverse("user_password_reset_confirm", kwargs={"uidb64": uid, "token": token}), data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "비밀번호가 성공적으로 재설정되었습니다.")

    def test_password_reset_confirm_invalid_uid(self):
        """잘못된 UID"""
        data = {"new_password": "newpass123", "new_password_confirm": "newpass123"}
        response = self.client.post(
            reverse("user_password_reset_confirm", kwargs={"uidb64": "invalid_uid", "token": "fake_token"}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "잘못된 링크입니다.")

    def test_password_reset_confirm_nonexistent_user(self):
        """존재하지 않는 사용자 ID"""
        fake_uid = urlsafe_base64_encode(force_bytes(99999))
        data = {"new_password": "newpass123", "new_password_confirm": "newpass123"}
        response = self.client.post(
            reverse("user_password_reset_confirm", kwargs={"uidb64": fake_uid, "token": "fake_token"}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "잘못된 링크입니다.")

    def test_password_reset_confirm_invalid_token(self):
        """잘못된 토큰"""
        user = User.objects.create_user(email="resettoken@example.com", name="토큰테스트", password="oldpass123")
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        data = {"new_password": "newpass123", "new_password_confirm": "newpass123"}
        response = self.client.post(
            reverse("user_password_reset_confirm", kwargs={"uidb64": uid, "token": "invalid_token"}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "유효하지 않은 토큰입니다.")

    def test_password_reset_confirm_invalid_data(self):
        """잘못된 데이터"""
        user = User.objects.create_user(email="resetdata@example.com", name="데이터테스트", password="oldpass123")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        data = {"new_password": "short"}  # 잘못된 비밀번호
        response = self.client.post(
            reverse("user_password_reset_confirm", kwargs={"uidb64": uid, "token": token}), data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_serializer_password_mismatch(self):
        """비밀번호 불일치 - ValidationError 발생"""
        from apps.users.serializers import PasswordResetConfirmSerializer

        data = {"new_password": "newpassword123!", "new_password_confirm": "differentpassword123!"}
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password_confirm", serializer.errors)
        self.assertEqual(serializer.errors["new_password_confirm"][0], "비밀번호가 일치하지 않습니다.")


class AdminAPITest(TestCase):
    """관리자 API 테스트"""

    def setUp(self):
        # 기존 사용자 모두 삭제하여 격리 보장
        User.objects.all().delete()

        self.client = APIClient()
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            name="관리자",
            password="adminpass123",
            is_admin=True,
        )
        # 일반 사용자 생성
        self.normal_user = User.objects.create_user(
            email="user@example.com", name="일반 사용자", password="userpass123"
        )

    # admin_user_list 함수 테스트 (라인 19-26)
    def test_admin_user_list_with_admin(self):
        """관리자 권한으로 사용자 목록 조회"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션된 응답에서 실제 사용자 수 확인
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["count"], 2)

    def test_admin_user_list_with_normal_user(self):
        """일반 사용자가 관리자 API 접근 시도 - 라인 21-22"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("admin_user_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "관리자만 접근 가능합니다.")

    # check_admin_permission 메서드 테스트 (라인 34-37)
    def test_check_admin_permission_with_normal_user_get(self):
        """일반 사용자가 GET 요청 시 권한 체크"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("admin_user_detail", args=[self.admin_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "관리자만 접근 가능합니다.")

    def test_check_admin_permission_with_normal_user_put(self):
        """일반 사용자가 PUT 요청 시 권한 체크"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("admin_user_detail", args=[self.admin_user.id])
        data = {"name": "해킹 시도"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "관리자만 접근 가능합니다.")

    def test_check_admin_permission_with_normal_user_delete(self):
        """일반 사용자가 DELETE 요청 시 권한 체크"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("admin_user_detail", args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "관리자만 접근 가능합니다.")

    # AdminUserDetailView GET 메서드 테스트 (라인 39-45)
    def test_admin_user_detail_get_success(self):
        """관리자가 사용자 상세 조회 성공"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_detail", args=[self.normal_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.normal_user.email)
        self.assertEqual(response.data["name"], self.normal_user.name)

    def test_admin_user_detail_get_not_found(self):
        """존재하지 않는 사용자 조회 시 404"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_user_detail_put_user_success(self):
        """관리자가 사용자 정보 수정 성공"""
        self.client.force_authenticate(user=self.admin_user)

        target_user = User.objects.create(
            email="target@example.com", name="Target User", is_active=True, is_social=True
        )

        response = self.client.put(f"/api/admin/users/{target_user.id}/", {"is_active": False}, format="json")
        self.assertEqual(response.status_code, 200)
        target_user.refresh_from_db()
        self.assertFalse(target_user.is_active)

    def test_admin_user_detail_put_not_found(self):
        """관리자가 존재하지 않는 사용자 수정 시도 시 404"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_detail", args=[9999])
        data = {"name": "존재하지 않음"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # AdminUserDetailView DELETE 메서드 테스트 (라인 58-70)
    def test_admin_user_detail_delete_success(self):
        """관리자가 다른 사용자 삭제 성공 - 라인 66-67"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_detail", args=[self.normal_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("삭제되었습니다", response.data["message"])
        self.assertFalse(User.objects.filter(id=self.normal_user.id).exists())

    def test_admin_user_detail_delete_self_forbidden(self):
        """관리자가 자기 자신 삭제 시도 시 400 에러 - 라인 63-64"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_detail", args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "자기 자신은 삭제할 수 없습니다.")
        # 실제로 삭제되지 않았는지 확인
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())

    def test_admin_user_detail_delete_not_found(self):
        """존재하지 않는 사용자 삭제 시도 시 404"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_user_detail", args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # IsAdmin 클래스 테스트 (라인 14-15) - 직접 테스트
    def test_is_admin_permission_class(self):
        """IsAdmin 클래스의 has_permission 메서드 직접 테스트"""
        from apps.users.admin_views import IsAdmin

        permission = IsAdmin()

        # Mock request 객체 생성
        class MockRequest:
            def __init__(self, user):
                self.user = user

        # 관리자 사용자 테스트
        admin_request = MockRequest(self.admin_user)
        self.assertTrue(permission.has_permission(admin_request, None))

        # 일반 사용자 테스트
        normal_request = MockRequest(self.normal_user)
        self.assertFalse(permission.has_permission(normal_request, None))

    def test_admin_user_detail_put_invalid_data(self):
        """관리자가 잘못된 데이터로 사용자 수정 시도"""
        self.client.force_authenticate(user=self.admin_user)

        target_user = User.objects.create(
            email="target@example.com", name="Target User", is_active=True, is_social=True
        )

        # is_active에 잘못된 타입 전송 (문자열 대신 불린이어야 함)
        invalid_data = {"is_active": "invalid_boolean_value"}

        response = self.client.put(f"/api/admin/users/{target_user.id}/", invalid_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("is_active", response.data)


class ChangePasswordTest(TestCase):
    """비밀번호 변경 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", name="테스트 사용자", password="oldpassword123")
        self.social_user = User.objects.create_user(email="social@example.com", name="소셜 사용자", is_social=True)
        self.change_password_url = "/api/user/change-password/"

    def test_change_password_success(self):
        """비밀번호 변경 성공 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
            "new_password_confirm": "newpassword456",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # 새 비밀번호로 로그인 확인
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword456"))

    def test_change_password_wrong_old_password(self):
        """잘못된 기존 비밀번호 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword456",
            "new_password_confirm": "newpassword456",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

        # 기존 비밀번호 그대로 유지 확인
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))

    def test_change_password_mismatch(self):
        """새 비밀번호 불일치 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
            "new_password_confirm": "differentpassword",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password_confirm", response.data)

    def test_change_password_weak_password(self):
        """약한 비밀번호 테스트 (Django validation)"""
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "oldpassword123",
            "new_password": "123",  # 너무 짧은 비밀번호
            "new_password_confirm": "123",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_social_user(self):
        """소셜 사용자 비밀번호 변경 시도 테스트"""
        self.client.force_authenticate(user=self.social_user)
        data = {
            "old_password": "anypassword",
            "new_password": "newpassword456",
            "new_password_confirm": "newpassword456",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("소셜 로그인 사용자", response.data["error"])

    def test_change_password_unauthenticated(self):
        """인증되지 않은 사용자 테스트"""
        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
            "new_password_confirm": "newpassword456",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_missing_fields(self):
        """필수 필드 누락 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "oldpassword123",
            # new_password 누락
            "new_password_confirm": "newpassword456",
        }
        response = self.client.put(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
