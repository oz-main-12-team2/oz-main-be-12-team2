from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "password", "password_confirm", "address"]
        extra_kwargs = {
            "address": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False  # 이메일 인증 전까지 비활성화
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "address", "is_admin", "created_at", "updated_at"]
        read_only_fields = ["email", "is_admin", "created_at", "updated_at"]


class AdminUserSerializer(serializers.ModelSerializer):
    """관리자용 사용자 조회 serializer"""

    class Meta:
        model = User
        fields = ["id", "email", "name", "address", "is_admin", "is_social", "is_active", "created_at", "updated_at"]
        read_only_fields = ["email", "created_at", "updated_at"]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """관리자용 사용자 수정 serializer"""

    class Meta:
        model = User
        fields = ["is_active"]


class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 serializer"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "새 비밀번호가 일치하지 않습니다."})

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"new_password": "새 비밀번호는 기존 비밀번호와 달라야 합니다."})

        return attrs


# 비밀번호 재설정 serializer
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "비밀번호가 일치하지 않습니다."})
        return attrs


class UserLoginSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name"]
