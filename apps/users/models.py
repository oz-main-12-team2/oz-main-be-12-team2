from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from apps.utils.models import TimestampModel


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        if not name:
            raise ValueError("이름은 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)

        # 소셜 로그인이 아닌 경우에만 password 설정
        if not extra_fields.get("is_social", False):
            if not password:
                raise ValueError("일반 회원가입 시 비밀번호는 필수입니다.")
            user.set_password(password)
        else:
            user.password = None

        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_social", False)  # superuser는 소셜 로그인 불가

        if not password:
            raise ValueError("슈퍼유저는 비밀번호가 필수입니다.")

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampModel):
    email = models.EmailField(max_length=255, unique=True, verbose_name="이메일")
    name = models.CharField(max_length=100, verbose_name="이름")
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name="비밀번호")
    address = models.CharField(max_length=100, blank=True, verbose_name="주소")
    is_admin = models.BooleanField(default=False, verbose_name="관리자 여부")
    is_social = models.BooleanField(default=False, verbose_name="소셜 회원가입 여부")
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        """Django Admin 접근 권한을 is_admin과 연동"""
        return self.is_admin

    def save(self, *args, **kwargs):
        # 소셜 로그인 사용자의 경우 password를 None으로 설정
        if self.is_social:
            self.password = None
        # 일반 사용자인데 password가 없는 경우 검증
        elif not self.password and not self.pk:  # 신규 생성 시에만 체크
            raise ValidationError("일반 회원가입 시 비밀번호는 필수입니다.")

        super().save(*args, **kwargs)

    def clean(self):
        """모델 유효성 검증"""
        super().clean()

        if not self.is_social and not self.password:
            raise ValidationError({"password": "일반 회원가입 시 비밀번호는 필수입니다."})
