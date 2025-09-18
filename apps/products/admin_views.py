from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


# 상품 등록 (POST)
@swagger_auto_schema(method="post", request_body=ProductSerializer)
@api_view(["POST"])
def admin_product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "상품이 생성되었습니다."}, status=status.HTTP_201_CREATED)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# 상품 수정 (PUT)
@swagger_auto_schema(method="put", request_body=ProductSerializer)
@api_view(["PUT"])
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product, data=request.data, partial=False)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "상품이 수정되었습니다."}, status=status.HTTP_200_OK)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# 상품 삭제 (DELETE)
@api_view(["DELETE"])
def admin_product_delete(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response({"message": "상품이 삭제되었습니다"}, status=200)
    except Product.DoesNotExist:
        return Response({"message": "상품을 찾을 수 없습니다"}, status=404)
