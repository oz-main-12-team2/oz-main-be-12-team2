# django-allauth 추가 설정용 파일
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # 소셜 계정 데이터에서 이름 정보 추출
        extra_data = sociallogin.account.extra_data

        if sociallogin.account.provider == "google":
            user.name = extra_data.get("name", "")
        elif sociallogin.account.provider == "naver":
            user.name = extra_data.get("name", "")

        user.is_social = True
        user.save()
        return user
