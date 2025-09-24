from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.support.models import FAQ, Inquiry
from apps.users.models import User


class AdminInquiryListAPIViewTest(APITestCase):
    def setUp(self):
        # 기존 데이터 정리
        Inquiry.objects.all().delete()
        User.objects.all().delete()

        self.client = APIClient()

        # 일반 사용자
        self.user = User.objects.create_user(
            email="user@example.com", name="일반유저", password="testpass123", is_active=True, is_admin=False
        )

        # 관리자 사용자
        self.admin_user = User.objects.create_user(
            email="admin@example.com", name="관리자", password="testpass123", is_active=True, is_admin=True
        )

        # 테스트 문의 데이터
        self.inquiry1 = Inquiry.objects.create(
            user=self.user, category="order", title="주문 문의", content="주문 관련 내용", status="submitted"
        )

        self.inquiry2 = Inquiry.objects.create(
            user=self.user, category="payment", title="결제 문의", content="결제 관련 내용", status="completed"
        )

        self.url = reverse("admin-inquiry-list")  # URL 이름 확인 필요

    def test_unauthenticated_access(self):
        """인증되지 않은 접근 테스트"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_access_forbidden(self):
        """일반 사용자 접근 금지 테스트"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "관리자만 접근 가능합니다.")

    def test_admin_access_success(self):
        """관리자 접근 성공 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_by_status(self):
        """상태별 필터링 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"{self.url}?status=submitted")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "submitted")

    def test_filter_by_nonexistent_status(self):
        """존재하지 않는 상태로 필터링"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"{self.url}?status=nonexistent")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class AdminInquiryDetailUpdateAPIViewTest(APITestCase):
    def setUp(self):
        # 기존 데이터 정리
        Inquiry.objects.all().delete()
        User.objects.all().delete()

        self.client = APIClient()

        # 일반 사용자
        self.user = User.objects.create_user(
            email="user@example.com", name="일반유저", password="testpass123", is_active=True, is_admin=False
        )

        # 관리자 사용자
        self.admin_user = User.objects.create_user(
            email="admin@example.com", name="관리자", password="testpass123", is_active=True, is_admin=True
        )

        # 테스트 문의
        self.inquiry = Inquiry.objects.create(
            user=self.user, category="order", title="테스트 문의", content="테스트 내용", status="submitted"
        )

        self.url = reverse("admin-inquiry-detail-update", kwargs={"pk": self.inquiry.pk})

    def test_unauthenticated_retrieve(self):
        """인증 없이 조회 시도"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_retrieve_forbidden(self):
        """일반 사용자 조회 금지"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "관리자만 접근 가능합니다.")

    def test_admin_retrieve_success(self):
        """관리자 조회 성공"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.inquiry.id)
        self.assertEqual(response.data["title"], "테스트 문의")

    def test_non_admin_update_forbidden(self):
        """일반 사용자 수정 금지"""
        self.client.force_authenticate(user=self.user)
        data = {"status": "completed"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_put_update_forbidden(self):
        """일반 사용자 PUT 수정 금지"""
        self.client.force_authenticate(user=self.user)
        data = {"status": "completed"}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_update_success(self):
        """관리자 상태 수정 성공"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"status": "completed"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DB에서 확인
        self.inquiry.refresh_from_db()
        self.assertEqual(self.inquiry.status, "completed")

    def test_admin_put_update_success(self):
        """관리자 PUT 수정 성공"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"status": "in_progress"}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_status(self):
        """잘못된 상태로 수정 시도"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"status": "invalid_status"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminFAQListCreateAPIViewTest(APITestCase):
    def setUp(self):
        # 기존 데이터 정리
        FAQ.objects.all().delete()
        User.objects.all().delete()

        self.client = APIClient()

        # 일반 사용자
        self.user = User.objects.create_user(
            email="user@example.com", name="일반유저", password="testpass123", is_active=True, is_admin=False
        )

        # 관리자 사용자
        self.admin_user = User.objects.create_user(
            email="admin@example.com", name="관리자", password="testpass123", is_active=True, is_admin=True
        )

        # 테스트 FAQ
        self.faq = FAQ.objects.create(
            category="order", question="테스트 질문", answer="테스트 답변", is_active=True, order=1
        )

        self.url = reverse("admin-faq-list-create")

    def test_non_admin_list_forbidden(self):
        """일반 사용자 FAQ 목록 조회 금지"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_list_success(self):
        """관리자 FAQ 목록 조회 성공"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_non_admin_create_forbidden(self):
        """일반 사용자 FAQ 생성 금지"""
        self.client.force_authenticate(user=self.user)
        data = {"category": "payment", "question": "새로운 질문", "answer": "새로운 답변"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_success(self):
        """관리자 FAQ 생성 성공"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"category": "payment", "question": "새로운 질문", "answer": "새로운 답변", "order": 2}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question"], "새로운 질문")

        # DB에서 확인
        faq = FAQ.objects.get(question="새로운 질문")
        self.assertEqual(faq.category, "payment")
        self.assertTrue(faq.is_active)  # 기본값

    def test_create_invalid_data(self):
        """잘못된 데이터로 FAQ 생성"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"category": "invalid_category", "question": "", "answer": "답변"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminFAQDetailUpdateDeleteAPIViewTest(APITestCase):
    def setUp(self):
        # 기존 데이터 정리
        FAQ.objects.all().delete()
        User.objects.all().delete()

        self.client = APIClient()

        # 일반 사용자
        self.user = User.objects.create_user(
            email="user@example.com", name="일반유저", password="testpass123", is_active=True, is_admin=False
        )

        # 관리자 사용자
        self.admin_user = User.objects.create_user(
            email="admin@example.com", name="관리자", password="testpass123", is_active=True, is_admin=True
        )

        # 테스트 FAQ
        self.faq = FAQ.objects.create(
            category="order", question="테스트 질문", answer="테스트 답변", is_active=True, order=1
        )

        self.url = reverse("admin-faq-detail-update-delete", kwargs={"pk": self.faq.pk})

    def test_non_admin_retrieve_forbidden(self):
        """일반 사용자 FAQ 조회 금지"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_retrieve_success(self):
        """관리자 FAQ 조회 성공"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question"], "테스트 질문")

    def test_admin_update_success(self):
        """관리자 FAQ 수정 성공"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"question": "수정된 질문", "answer": "수정된 답변", "category": "payment", "is_active": False}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DB에서 확인
        self.faq.refresh_from_db()
        self.assertEqual(self.faq.question, "수정된 질문")
        self.assertFalse(self.faq.is_active, False)

    def test_admin_put_update_success(self):
        """관리자 FAQ PUT 수정 성공"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "category": "shipping",
            "question": "완전히 새로운 질문",
            "answer": "완전히 새로운 답변",
            "is_active": True,
            "order": 5,
        }
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_delete_forbidden(self):
        """일반 사용자 FAQ 삭제 금지"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_delete_success(self):
        """관리자 FAQ 삭제 성공"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # DB에서 확인
        self.assertFalse(FAQ.objects.filter(pk=self.faq.pk).exists())

    def test_delete_nonexistent_faq(self):
        """존재하지 않는 FAQ 삭제"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin-faq-detail-update-delete", kwargs={"pk": 9999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_admin_put_update_forbidden(self):
        """일반 사용자 PUT 수정 금지"""
        self.client.force_authenticate(user=self.user)
        data = {"question": "수정 시도", "answer": "답변", "category": "order"}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_patch_update_forbidden(self):
        """일반 사용자 PATCH 수정 금지"""
        self.client.force_authenticate(user=self.user)
        data = {"question": "수정 시도"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
