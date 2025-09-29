from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"  # 사용자가 ?page_size=20 지정 가능
