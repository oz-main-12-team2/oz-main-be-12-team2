from google import genai
from django.conf import settings


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate_auto_reply(self, question, category):
        category_map = {
            "order": "주문",
            "shipping": "배송",
            "product": "상품",
            "payment": "결제/환불",
            "account": "회원정보",
            "other": "기타",
        }

        prompt = f"""
        고객 문의 카테고리: {category_map.get(category, "기타")}
        고객 문의 내용: {question}

        당신은 책쇼핑몰 고객센터 담당입니다.
        위 문의에 대해 친절한 답변을 한국어로 작성해주세요.
        답변은 200자 이내로 간결하게 작성하고, 고객서비스 톤앤매너를 유지해주세요.
        """

        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            return response.text
        except Exception:
            return "문의해 주셔서 감사합니다. 빠른 시일 내에 답변드리겠습니다."


gemini_service = GeminiService()
