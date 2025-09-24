from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.support.models import FAQ, Inquiry, InquiryReply

User = get_user_model()


class InquiryListCreateAPIViewTest(APITestCase):
    def setUp(self):
        # 기존 데이터 정리
        Inquiry.objects.all().delete()
        InquiryReply.objects.all().delete()
        User.objects.all().delete()

        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", name="테스트유저", password="testpass123", is_active=True
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", name="다른유저", password="testpass123", is_active=True
        )
        self.inquiry = Inquiry.objects.create(
            user=self.user, category="order", title="테스트 문의", content="테스트 문의 내용"
        )
        self.other_inquiry = Inquiry.objects.create(
            user=self.other_user, category="product", title="다른 사용자 문의", content="다른 사용자 문의 내용"
        )
        self.url = reverse("inquiry-list-create")

    def test_unauthenticated_access(self):
        """인증되지 않은 사용자의 접근 테스트"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_inquiry_list_authenticated(self):
        """인증된 사용자의 문의 목록 조회"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "테스트 문의")

    def test_get_inquiry_list_filters_by_user(self):
        """문의 목록이 현재 사용자로 필터링되는지 테스트"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.inquiry.id)

    @patch("apps.support.serializers.gemini_service.generate_auto_reply")
    def test_create_inquiry_success(self, mock_ai_reply):
        """문의 생성 성공 테스트"""
        mock_ai_reply.return_value = "AI 자동 응답입니다."

        self.client.force_authenticate(user=self.user)
        data = {"category": "payment", "title": "새로운 문의", "content": "새로운 문의 내용"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 문의가 생성되었는지 확인
        inquiry = Inquiry.objects.get(title="새로운 문의")
        self.assertEqual(inquiry.user, self.user)
        self.assertEqual(inquiry.status, "completed")

        # AI 답변이 생성되었는지 확인
        self.assertTrue(inquiry.replies.exists())
        ai_reply = inquiry.replies.first()
        self.assertTrue(ai_reply.is_admin_reply)
        self.assertIsNone(ai_reply.author)

        mock_ai_reply.assert_called_once_with("새로운 문의 내용", "payment")

    def test_create_inquiry_invalid_data(self):
        """잘못된 데이터로 문의 생성 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {"category": "invalid_category", "title": "", "content": "내용"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inquiry_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        self.client.force_authenticate(user=self.user)
        data = {"category": "order"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class InquiryDetailAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", name="테스트유저", password="testpass123", is_active=True
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", name="다른유저", password="testpass123", is_active=True
        )
        self.inquiry = Inquiry.objects.create(
            user=self.user, category="order", title="테스트 문의", content="테스트 문의 내용"
        )
        self.other_inquiry = Inquiry.objects.create(
            user=self.other_user, category="product", title="다른 사용자 문의", content="다른 사용자 문의 내용"
        )

        # 답변 생성
        InquiryReply.objects.create(inquiry=self.inquiry, content="관리자 답변", is_admin_reply=True)

        self.url = reverse("inquiry-detail", kwargs={"pk": self.inquiry.pk})
        self.other_url = reverse("inquiry-detail", kwargs={"pk": self.other_inquiry.pk})

    def test_unauthenticated_access(self):
        """인증되지 않은 접근 테스트"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_inquiry_detail_success(self):
        """본인의 문의 상세 조회 성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.inquiry.id)
        self.assertEqual(response.data["title"], "테스트 문의")
        self.assertEqual(len(response.data["replies"]), 1)

    def test_get_other_user_inquiry_forbidden(self):
        """다른 사용자의 문의 조회 시 404"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.other_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_inquiry(self):
        """존재하지 않는 문의 조회"""
        self.client.force_authenticate(user=self.user)
        url = reverse("inquiry-detail", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FAQListAPIViewTest(APITestCase):
    def setUp(self):
        # 기존 데이터 정리
        FAQ.objects.all().delete()

        self.client = APIClient()
        self.active_faq = FAQ.objects.create(
            category="order", question="주문은 어떻게 하나요?", answer="주문 방법입니다.", is_active=True, order=1
        )
        self.inactive_faq = FAQ.objects.create(
            category="payment", question="비활성 FAQ", answer="비활성 FAQ 답변", is_active=False, order=2
        )
        self.product_faq = FAQ.objects.create(
            category="product", question="상품 문의", answer="상품 답변", is_active=True, order=3
        )
        self.url = reverse("faq-list")

    def test_get_faq_list_unauthenticated(self):
        """인증 없이 FAQ 조회 가능"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_active_faqs_only(self):
        """활성화된 FAQ만 조회"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # 변경

        titles = [faq["question"] for faq in response.data["results"]]  # 변경
        self.assertIn("주문은 어떻게 하나요?", titles)
        self.assertNotIn("비활성 FAQ", titles)

    def test_filter_faq_by_category(self):
        """카테고리별 FAQ 필터링"""
        response = self.client.get(self.url + "?category=order")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # 변경
        self.assertEqual(response.data["results"][0]["question"], "주문은 어떻게 하나요?")  # 변경

    def test_filter_faq_nonexistent_category(self):
        """존재하지 않는 카테고리 필터링"""
        response = self.client.get(self.url + "?category=nonexistent")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)  # 변경

    def test_faq_ordering(self):
        """FAQ 정렬 확인 (order, -created_at)"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["order"], 1)  # 변경


class InquiryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", name="테스트유저", password="testpass123", is_active=True
        )

    def test_inquiry_creation(self):
        """문의 생성 테스트"""
        inquiry = Inquiry.objects.create(user=self.user, category="order", title="테스트 문의", content="테스트 내용")

        self.assertEqual(inquiry.status, "submitted")  # 기본값
        self.assertEqual(str(inquiry), "테스트 문의 - test@example.com")

    def test_inquiry_category_choices(self):
        """카테고리 선택지 테스트"""
        valid_categories = ["order", "shipping", "product", "payment", "account", "other"]

        for category in valid_categories:
            inquiry = Inquiry.objects.create(
                user=self.user, category=category, title=f"{category} 문의", content="테스트"
            )
            self.assertEqual(inquiry.category, category)


class FAQModelTest(TestCase):
    def test_faq_creation(self):
        """FAQ 생성 테스트"""
        faq = FAQ.objects.create(category="order", question="테스트 질문", answer="테스트 답변")

        self.assertTrue(faq.is_active)  # 기본값
        self.assertEqual(faq.order, 0)  # 기본값
        self.assertEqual(str(faq), "테스트 질문")

    def test_faq_ordering(self):
        """FAQ 정렬 테스트"""
        FAQ.objects.create(category="order", question="질문1", answer="답변1", order=2)
        faq2 = FAQ.objects.create(category="order", question="질문2", answer="답변2", order=1)

        faqs = list(FAQ.objects.all())
        self.assertEqual(faqs[0], faq2)  # order가 작은 것이 먼저


class InquiryReplyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", name="테스트유저", password="testpass123", is_active=True
        )
        self.inquiry = Inquiry.objects.create(
            user=self.user, category="order", title="테스트 문의", content="테스트 내용"
        )

    def test_inquiry_reply_creation(self):
        """문의 답변 생성 테스트"""
        reply = InquiryReply.objects.create(inquiry=self.inquiry, content="답변 내용", is_admin_reply=True)

        self.assertTrue(reply.is_admin_reply)  # is_admin_reply=True로 생성했으므로
        self.assertIsNone(reply.author)

    def test_inquiry_reply_with_author(self):
        """작성자가 있는 답변 테스트"""
        reply = InquiryReply.objects.create(inquiry=self.inquiry, author=self.user, content="사용자 답변")

        expected_str = f"{self.inquiry.title} 답변 - {self.user.email}"
        self.assertEqual(str(reply), expected_str)

    def test_inquiry_reply_without_author(self):
        """작성자가 없는 답변 테스트 (AI 답변)"""
        reply = InquiryReply.objects.create(inquiry=self.inquiry, content="AI 답변", is_admin_reply=True)

        expected_str = f"{self.inquiry.title} 답변 - 상담원 제미나이"
        self.assertEqual(str(reply), expected_str)
