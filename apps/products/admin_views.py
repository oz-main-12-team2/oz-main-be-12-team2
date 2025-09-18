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


@swagger_auto_schema(
    method="get",
    responses={200: ProductSerializer},
)
@swagger_auto_schema(
    method="put",
    request_body=ProductSerializer,
)
@api_view(["GET", "PUT", "DELETE"])
def admin_product_detail_update_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # 상세 조회
    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 수정
    elif request.method == "PUT":
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "상품이 수정되었습니다."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # 삭제
    elif request.method == "DELETE":
        product.delete()
        return Response({"message": "상품이 삭제되었습니다."}, status=status.HTTP_200_OK)
