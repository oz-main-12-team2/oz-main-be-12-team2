from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Cart

User = get_user_model()


# 사용자 생성시 장바구니 자동 생성
@receiver(post_save, sender=User)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created:  # 새 유저일 경우만 실행
        Cart.objects.create(user=instance)
