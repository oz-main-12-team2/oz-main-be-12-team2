from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password_confirm', 'address']
        extra_kwargs = {
            'address': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '비밀번호가 일치하지 않습니다.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SocialSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'address']
        extra_kwargs = {
            'address': {'required': False},
        }

    def create(self, validated_data):
        validated_data['is_social'] = True
        user = User(**validated_data)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'address', 'created_at']
        read_only_fields = ['email', 'created_at']

class AdminUserSerializer(serializers.ModelSerializer):
    """관리자용 사용자 조회 serializer"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'address', 'is_admin', 'is_social', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """관리자용 사용자 수정 serializer"""
    class Meta:
        model = User
        fields = ['name', 'address', 'is_admin']