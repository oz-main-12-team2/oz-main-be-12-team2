from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "author",
            "publisher",
            "price",
            "stock",
            "category",
            "image_url",
        ]
        labels = {
            "name": "상품명",
            "description": "상품 설명",
            "author": "저자",
            "publisher": "출판사",
            "price": "가격",
            "stock": "재고",
            "category": "카테고리",
            "image_url": "이미지 URL",
        }
