from locust import HttpUser, between, task


class ApiUser(HttpUser):
    wait_time = between(1, 3)  # 요청 간 1-3초 대기

    def on_start(self):
        """테스트 시작 시 한 번 실행"""
        print("API 테스트 시작")

    @task(4)
    def view_products_list(self):
        """상품 목록 조회"""
        with self.client.get("/api/products/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"응답 코드: {response.status_code}")

    @task(2)
    def view_cart_list(self):
        """장바구니 조회"""
        with self.client.get("/api/cart/", catch_response=True) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"응답 코드: {response.status_code}")

    @task(2)
    def view_orders_list(self):
        """주문 목록 조회"""
        with self.client.get("/api/orders/", catch_response=True) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"응답 코드: {response.status_code}")

    @task(1)
    def view_faqs(self):
        """FAQ 목록 조회"""
        with self.client.get("/api/support/faqs/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"응답 코드: {response.status_code}")

    @task(1)
    def view_inquiries(self):
        """문의 목록 조회"""
        with self.client.get("/api/support/inquiries/", catch_response=True) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"응답 코드: {response.status_code}")
