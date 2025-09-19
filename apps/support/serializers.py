from rest_framework import serializers

from .models import FAQ, Inquiry, InquiryReply


class InquiryReplySerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = InquiryReply
        fields = ['id', 'content', 'is_admin_reply', 'created_at', 'author_username']
        read_only_fields = ['id', 'created_at', 'author_username']


class InquiryListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = ['id', 'category', 'category_display', 'title', 'status',
                  'status_display', 'created_at', 'reply_count']
        read_only_fields = ['id', 'created_at']

    def get_reply_count(self, obj):
        return obj.replies.count()


class InquiryDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    replies = InquiryReplySerializer(many=True, read_only=True)

    class Meta:
        model = Inquiry
        fields = ['id', 'category', 'category_display', 'title', 'content',
                  'status', 'status_display', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['category', 'title', 'content']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class InquiryReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryReply
        fields = ['content']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['inquiry_id'] = self.context['inquiry_id']
        # 관리자인지 확인
        validated_data['is_admin_reply'] = self.context['request'].user.is_staff
        return super().create(validated_data)


class FAQSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = FAQ
        fields = ['id', 'category', 'category_display', 'question', 'answer', 'order']
        read_only_fields = ['id']