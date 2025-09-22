from rest_framework import serializers

from .gemini_service import gemini_service
from .models import FAQ, Inquiry, InquiryReply


class InquiryReplySerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = InquiryReply
        fields = ["id", "content", "is_admin_reply", "created_at", "author_username"]
        read_only_fields = ["id", "created_at", "author_username"]


class InquiryListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = [
            "id",
            "category",
            "category_display",
            "title",
            "status",
            "status_display",
            "created_at",
            "reply_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_reply_count(self, obj):
        return obj.replies.count()


class InquiryDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    replies = InquiryReplySerializer(many=True, read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            "id",
            "category",
            "category_display",
            "title",
            "content",
            "status",
            "status_display",
            "created_at",
            "updated_at",
            "replies",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["category", "title", "content"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        inquiry = super().create(validated_data)

        # 문의 생성 즉시 AI 자동응답 생성
        ai_reply_content = gemini_service.generate_auto_reply(inquiry.content, inquiry.category)

        InquiryReply.objects.create(inquiry=inquiry, content=ai_reply_content, is_admin_reply=True, author=None)

        inquiry.status = "completed"
        inquiry.save()

        return inquiry


class FAQSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = FAQ
        fields = ["id", "category", "category_display", "question", "answer", "order", "is_active"]
        read_only_fields = ["id"]


class AdminInquiryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["status"]
        read_only_fields = ["id", "category", "title", "content", "user", "created_at", "updated_at"]
