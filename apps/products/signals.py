from datetime import datetime

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Product


@receiver(post_save, sender=Product)
def rename_product_image_on_create(sender, instance, created, **kwargs):
    """
    상품 생성 시 pk + 타임스탬프 기반으로 파일명 변경
    """
    if created and instance.image:
        ext = instance.image.name.split(".")[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"products/{instance.pk}_{timestamp}.{ext}"

        # 파일명이 원하는 규칙과 다르면 rename 후 다시 저장
        if not instance.image.name.endswith(new_filename):
            instance.image.name = new_filename
            instance.save(update_fields=["image"])  # ✅ 파일명 갱신


@receiver(pre_save, sender=Product)
def update_product_image_filename(sender, instance, **kwargs):
    """
    상품 이미지 저장 전에 pk 기반 + 타임스탬프 파일명으로 교체
    """
    if not instance.pk or not instance.image:
        return  # 신규 생성인데 아직 pk 없음 or 이미지 없음

    try:
        old_image = Product.objects.get(pk=instance.pk).image
    except Product.DoesNotExist:
        old_image = None

    # 기존 이미지와 다른 경우
    if instance.image and (not old_image or old_image != instance.image):
        ext = instance.image.name.split(".")[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        instance.image.name = f"products/{instance.pk}_{timestamp}.{ext}"

        # 기존 파일은 삭제
        if old_image and old_image != instance.image:
            old_image.delete(save=False)


@receiver(post_delete, sender=Product)
def delete_product_image_on_delete(sender, instance, **kwargs):
    """
    상품 삭제 시 S3 이미지도 삭제
    """
    if instance.image:
        instance.image.delete(save=False)
