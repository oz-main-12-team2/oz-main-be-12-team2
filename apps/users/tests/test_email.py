from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserEmailTests(TestCase):
    def test_register_sends_activation_email(self):
        """회원가입 시 인증 메일이 발송되는지 테스트"""
        data = {
            "email": "test@example.com",
            "name": "테스트유저",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = self.client.post(reverse("user_register"), data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)  # 메일이 1개 발송됐는지 확인
        self.assertIn("회원가입 이메일 인증", mail.outbox[0].subject)
        self.assertIn("test@example.com", mail.outbox[0].to)

    def test_password_reset_sends_email(self):
        """비밀번호 재설정 요청 시 메일 발송"""
        user = User.objects.create_user(email="reset@example.com", name="ResetUser", password="ResetPass123!")

        response = self.client.post(reverse("password_reset_request"), {"email": user.email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("비밀번호 재설정", mail.outbox[0].subject)
