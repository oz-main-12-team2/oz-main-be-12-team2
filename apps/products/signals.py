from datetime import datetime

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Product


@receiver(pre_save, sender=Product)
def update_product_image_filename(sender, instance, **kwargs):
    """
    상품 수정 시: 기존 이미지 삭제 + 새 파일명 적용
    """
    if not instance.pk or not instance.image:
        return  # 신규 생성인데 아직 pk 없음 or 이미지 없음

    try:
        old_instance = Product.objects.get(pk=instance.pk)
        old_image = old_instance.image
    except Product.DoesNotExist:
        old_image = None

    # 이미지가 변경된 경우에만 처리
    if instance.image and (not old_image or old_image.name != instance.image.name):
        ext = instance.image.name.split(".")[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        instance.image.name = f"products/{instance.pk}_{timestamp}.{ext}"

        if old_image and old_image.name and old_image != instance.image:
            try:
                old_image.delete(save=False)
            except Exception as e:
                print(f"[WARN] 기존 이미지 삭제 실패: {e}")


@receiver(post_save, sender=Product)
def rename_product_image_on_create(sender, instance, created, **kwargs):
    """
    상품 생성 시: pk가 생긴 이후 파일명 규칙 적용
    """
    if created and instance.image:
        ext = instance.image.name.split(".")[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"products/{instance.pk}_{timestamp}.{ext}"

        if instance.image.name != new_filename:
            # 파일을 강제로 다시 저장해서 S3에 업로드
            instance.image.storage.save(new_filename, instance.image.file)
            instance.image.name = new_filename
            instance.save(update_fields=["image"])


@receiver(post_delete, sender=Product)
def delete_product_image_on_delete(sender, instance, **kwargs):
    """
    상품 삭제 시 S3 이미지도 삭제
    """
    if instance.image:
        instance.image.delete(save=False)
