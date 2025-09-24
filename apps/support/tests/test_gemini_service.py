from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from apps.support.gemini_service import GeminiService, gemini_service


class GeminiServiceTest(TestCase):
    def setUp(self):
        self.service = GeminiService()

    @patch("apps.support.gemini_service.genai.Client")
    def test_init_configuration(self, mock_client):
        """서비스 초기화 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        service = GeminiService()

        mock_client.assert_called_once_with(api_key=settings.GEMINI_API_KEY)
        self.assertEqual(service.client, mock_client_instance)

    @patch("apps.support.gemini_service.genai.Client")
    def test_generate_auto_reply_success(self, mock_client):
        """자동 응답 생성 성공 테스트"""
        # Mock 설정
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "안녕하세요. 주문 문의에 대해 답변드립니다."
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        result = service.generate_auto_reply("주문은 언제 배송되나요?", "order")

        self.assertEqual(result, "안녕하세요. 주문 문의에 대해 답변드립니다.")
        mock_client_instance.models.generate_content.assert_called_once()

        # prompt 내용 확인
        call_kwargs = mock_client_instance.models.generate_content.call_args[1]
        prompt = call_kwargs["contents"]
        self.assertIn("주문", prompt)
        self.assertIn("주문은 언제 배송되나요?", prompt)
        self.assertIn("책쇼핑몰 고객센터", prompt)

    @patch("apps.support.gemini_service.genai.Client")
    def test_generate_auto_reply_all_categories(self, mock_client):
        """모든 카테고리별 응답 생성 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "자동 응답입니다."
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()

        categories = [
            ("order", "주문"),
            ("shipping", "배송"),
            ("product", "상품"),
            ("payment", "결제/환불"),
            ("account", "회원정보"),
            ("other", "기타"),
        ]

        for category_key, category_display in categories:
            result = service.generate_auto_reply(f"{category_display} 문의", category_key)
            self.assertEqual(result, "자동 응답입니다.")

            # 마지막 호출의 prompt 확인
            call_kwargs = mock_client_instance.models.generate_content.call_args[1]
            prompt = call_kwargs["contents"]
            self.assertIn(category_display, prompt)

    @patch("apps.support.gemini_service.genai.Client")
    def test_generate_auto_reply_unknown_category(self, mock_client):
        """알 수 없는 카테고리 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "기타 문의 응답입니다."
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        result = service.generate_auto_reply("기타 문의입니다", "unknown_category")

        self.assertEqual(result, "기타 문의 응답입니다.")

        # prompt에 "기타"가 포함되어야 함
        call_kwargs = mock_client_instance.models.generate_content.call_args[1]
        prompt = call_kwargs["contents"]
        self.assertIn("기타", prompt)

    @patch("apps.support.gemini_service.genai.Client")
    def test_generate_auto_reply_api_exception(self, mock_client):
        """API 호출 실패 시 기본 응답 반환 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.models.generate_content.side_effect = Exception("API Error")

        service = GeminiService()
        result = service.generate_auto_reply("테스트 질문", "order")

        self.assertEqual(result, "문의해 주셔서 감사합니다. 빠른 시일 내에 답변드리겠습니다.")

    @patch("apps.support.gemini_service.genai.Client")
    def test_generate_auto_reply_network_timeout(self, mock_client):
        """네트워크 타임아웃 예외 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.models.generate_content.side_effect = TimeoutError("Network timeout")

        service = GeminiService()
        result = service.generate_auto_reply("테스트 질문", "payment")

        self.assertEqual(result, "문의해 주셔서 감사합니다. 빠른 시일 내에 답변드리겠습니다.")

    @patch("apps.support.gemini_service.genai.Client")
    def test_generate_auto_reply_value_error(self, mock_client):
        """값 에러 예외 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.models.generate_content.side_effect = ValueError("Invalid input")

        service = GeminiService()
        result = service.generate_auto_reply("", "shipping")

        self.assertEqual(result, "문의해 주셔서 감사합니다. 빠른 시일 내에 답변드리겠습니다.")

    @patch("apps.support.gemini_service.genai.Client")
    def test_prompt_format_validation(self, mock_client):
        """프롬프트 형식 검증 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "응답"
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        service.generate_auto_reply("환불 가능한가요?", "payment")

        # prompt 구조 검증
        call_kwargs = mock_client_instance.models.generate_content.call_args[1]
        prompt = call_kwargs["contents"]
        self.assertIn("고객 문의 카테고리:", prompt)
        self.assertIn("고객 문의 내용:", prompt)
        self.assertIn("당신은 책쇼핑몰 고객센터 담당입니다.", prompt)
        self.assertIn("200자 이내", prompt)
        self.assertIn("한국어로", prompt)

    @patch("apps.support.gemini_service.genai.Client")
    def test_empty_question_handling(self, mock_client):
        """빈 질문 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "빈 질문에 대한 응답"
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        result = service.generate_auto_reply("", "order")

        self.assertEqual(result, "빈 질문에 대한 응답")

    @patch("apps.support.gemini_service.genai.Client")
    def test_long_question_handling(self, mock_client):
        """긴 질문 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "긴 질문에 대한 응답"
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        long_question = "매우 " * 100 + "긴 질문입니다."
        result = service.generate_auto_reply(long_question, "product")

        self.assertEqual(result, "긴 질문에 대한 응답")

        # 긴 질문이 프롬프트에 포함되는지 확인
        call_kwargs = mock_client_instance.models.generate_content.call_args[1]
        prompt = call_kwargs["contents"]
        self.assertIn(long_question, prompt)

    def test_singleton_instance(self):
        """싱글톤 인스턴스 테스트"""
        # gemini_service 인스턴스가 제대로 생성되었는지 확인
        self.assertIsInstance(gemini_service, GeminiService)
        self.assertIsNotNone(gemini_service.client)

    @patch("apps.support.gemini_service.genai.Client")
    def test_special_characters_in_question(self, mock_client):
        """특수문자가 포함된 질문 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "특수문자 질문 응답"
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        special_question = "주문번호 #12345, 가격 $50.99, 할인 50% 가능한가요?"
        result = service.generate_auto_reply(special_question, "order")

        self.assertEqual(result, "특수문자 질문 응답")

    @patch("apps.support.gemini_service.genai.Client")
    def test_none_category_handling(self, mock_client):
        """None 카테고리 처리 테스트"""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_response = MagicMock()
        mock_response.text = "None 카테고리 응답"
        mock_client_instance.models.generate_content.return_value = mock_response

        service = GeminiService()
        result = service.generate_auto_reply("질문입니다", None)

        self.assertEqual(result, "None 카테고리 응답")

        # None 카테고리는 "기타"로 처리되어야 함
        call_kwargs = mock_client_instance.models.generate_content.call_args[1]
        prompt = call_kwargs["contents"]
        self.assertIn("기타", prompt)
