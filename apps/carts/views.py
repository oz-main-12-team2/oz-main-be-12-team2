from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartProduct
from .serializers import CartProductSerializer, CartSerializer


# ✅ 장바구니 조회
class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


# ✅ 장바구니 상품 추가
class CartProductCreateView(generics.CreateAPIView):
    serializer_class = CartProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get(
            "quantity", 1
        )  # 데이터가 없으면 기본값 1

        cart_product, created = CartProduct.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        # 이미 있던 상품일 경우 수량 추가
        if not created:
            cart_product.quantity += quantity
            cart_product.save()

        serializer.instance = cart_product


# ✅ 장바구니 상품 수정(수량 변경) + 삭제
class CartProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ["put", "delete"]

    def get_queryset(self):
        return CartProduct.objects.filter(cart__user=self.request.user)

    # PUT 요청 처리 (수량 변경)
    def perform_update(self, serializer):
        quantity = serializer.validated_data.get("quantity")
        if quantity < 1:
            raise serializers.ValidationError("수량은 최소 1 이상이어야 합니다.")
        serializer.save()

    # DELETE 요청 처리 (상품 삭제)
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "상품이 장바구니에서 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


# ✅ 장바구니 전체 비우기
class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()  # 해당 장바구니에 담긴 상품 전체 삭제
            return Response({"detail": "장바구니가 비워졌습니다."}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "장바구니가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
