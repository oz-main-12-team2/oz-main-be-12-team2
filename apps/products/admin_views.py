import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from .forms import ProductForm
from .models import Product


# 상품 등록 (POST)
@api_view(["POST"])
def admin_product_create(request):
    # 1. request.body에서 JSON 데이터를 읽어옵니다.
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "잘못된 JSON 형식입니다."}, status=400
        )

    # 2. 읽어온 data로 Form을 초기화합니다.
    form = ProductForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse(
            {"success": True, "message": "상품이 생성되었습니다."}, status=201
        )
    else:
        # 유효성 검사 실패 시 에러 내용을 터미널에 출력
        print("CREATE FORM ERRORS:", form.errors.as_json())
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


# 상품 수정 (PUT)
@api_view(["PUT"])
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "잘못된 JSON 형식입니다."}, status=400
        )

    form = ProductForm(data, instance=product)

    if form.is_valid():
        form.save()
        return JsonResponse(
            {"success": True, "message": "상품이 수정되었습니다."}, status=200
        )
    else:
        # 유효성 검사 실패 시 에러 내용을 터미널에 출력
        print("CREATE FORM ERRORS:", form.errors.as_json())
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


# 상품 삭제 (DELETE)
@api_view(["DELETE"])
def admin_product_delete(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return JsonResponse(
            {"success": True, "message": "상품이 삭제되었습니다"}, status=200
        )
    except Product.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "상품을 찾을 수 없습니다"}, status=404
        )
