import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .forms import ProductForm
from .models import Product


# 상품 등록 (POST)
def admin_product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "상품이 등록되었습니다",
                    "product_id": product.id,
                },
                status=201,
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "유효하지 않은 데이터입니다.",
                    "errors": form.errors,
                },
                status=400,
            )
    return JsonResponse({"success": False, "message": "POST 요청만 허용됩니다."}, status=405)


# 상품 수정 (PUT)
@require_POST
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # PUT 요청을 처리하기 위해 request.body에서 JSON 데이터를 로드
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "잘못된 JSON 형식입니다."}, status=400)

    form = ProductForm(data, instance=product)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True, "message": "상품이 수정되었습니다."}, status=200)
    else:
        return JsonResponse(
            {
                "success": False,
                "message": "유효하지 않은 데이터입니다.",
                "errors": form.errors,
            },
            status=400,
        )


# 상품 삭제 (DELETE)
@require_POST
def admin_product_delete(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return JsonResponse({"success": True, "message": "상품이 삭제되었습니다"}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "상품을 찾을 수 없습니다"}, status=404)
