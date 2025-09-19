import os

import django
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# Django settings 초기화
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # 프로젝트에 맞게 수정
django.setup()


def check_email():
    subject = "이메일 발송 테스트"
    message = "이 메일은 환경변수 기반 설정이 잘 동작하는지 확인하는 테스트입니다."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.EMAIL_HOST_USER]  # 자기 자신에게 보내기

    print(f"📧 메일 발송 시도 중...\nFROM: {from_email}\nTO: {recipient_list}")
    sent_count = send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    if sent_count == 1:
        print("✅ 메일 발송 성공!")
    else:
        print("❌ 메일 발송 실패!")


if __name__ == "__main__":
    check_email()
