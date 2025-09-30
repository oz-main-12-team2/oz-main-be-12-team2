from django.db.models import Prefetch
from django.http import Http404
from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartProduct
from .serializers import CartProductSerializer, CartProductUpdateSerializer, CartSerializer


# ✅ 장바구니 조회
class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # 페이지네이션 제거
    filter_backends = []  # 정렬 제거

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related(
            Prefetch("items", queryset=CartProduct.objects.order_by("-id"))
        )


# ✅ 장바구니 상품 추가
class CartProductCreateView(generics.CreateAPIView):
    serializer_class = CartProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)  # 데이터가 없으면 기본값 1

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
    lookup_field = "product"  # product id를 받아서 수정/삭제

    http_method_names = ["put", "delete"]

    def get_queryset(self):
        return CartProduct.objects.filter(cart__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return CartProductUpdateSerializer  # ✅ 수량만
        return CartProductSerializer  # ✅ 삭제 시 응답에는 전체 정보

    # PUT 요청 처리 (수량 변경)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        # ✅ 요청 바디는 UpdateSerializer로 검증
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data.get("quantity")
        if quantity < 1:
            raise serializers.ValidationError("수량은 최소 1 이상이어야 합니다.")
        self.perform_update(serializer)

        # ✅ 응답은 전체 정보 포함하는 CartProductSerializer로 변환
        response_serializer = CartProductSerializer(instance)
        return Response(response_serializer.data)

    # DELETE 요청 처리 (상품 삭제)
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "상품이 장바구니에서 삭제되었습니다."},
            status=status.HTTP_200_OK
        )

    # 404 에러 메세지 커스텀
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="장바구니에 해당 상품이 없습니다.")


# ✅ 장바구니 전체 비우기
class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = Cart.objects.get(user=request.user)

        # 장바구니가 이미 비어있는 경우
        if not cart.items.exists():
            return Response(
                {"detail": "장바구니가 이미 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 장바구니 비우기
        cart.items.all().delete()
        return Response(
            {"detail": "장바구니가 비워졌습니다."},
            status=status.HTTP_200_OK,
        )
