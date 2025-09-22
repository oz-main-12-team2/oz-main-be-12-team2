from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")  # __str__ 은 모델에 정의된 대표 필드
