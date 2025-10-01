import random
import uuid
from typing import Optional

from apps.payments.models import PaymentStatus  # ✅ DB enum 사용

# 결제 상태 저장소 (실제 PG 대신 메모리에 저장)
_FAKE_PAYMENT_DB = {}  # {tx_id: {"amount": int, "method": str, "status": PaymentStatus }}


def process_payment(amount: int, method: str) -> dict:
    """
    💳 결제 요청 (모의 결제)
    - 요청 시 상태: PENDING
    - 현재는 즉시 SUCCESS/FAIL로 확정되지만, 실 PG 연동 시 웹훅에서 상태 변경
    """
    if amount <= 0:
        return {
            "status": PaymentStatus.FAIL.value,
            "transaction_id": None,
            "message": "결제 금액 오류",
        }

    tx_id = f"tx_{uuid.uuid4().hex[:12]}"

    # 1️⃣ 결제 요청: 우선 "대기" 상태 등록
    _FAKE_PAYMENT_DB[tx_id] = {
        "amount": amount,
        "method": method,
        "status": PaymentStatus.PENDING.value,
    }

    # 2️⃣ 현재는 즉시 결제 시도 결과를 반영 (실 PG에서는 webhook에서 처리됨)
    result = random.choices(
        population=[PaymentStatus.SUCCESS.value, PaymentStatus.FAIL.value],
        weights=[0.9, 0.1],
    )[0]

    _FAKE_PAYMENT_DB[tx_id]["status"] = result
    message = "결제 성공" if result == PaymentStatus.SUCCESS.value else "결제 실패"

    return {
        "status": result,
        "transaction_id": tx_id,
        "message": message,
    }


def cancel_payment(transaction_id: str) -> dict:
    """
    ❌ 결제 취소 (상태 전이 조건 반영)
    - ✅ PENDING: 아직 확정되지 않은 결제 → 취소 가능
    - ✅ SUCCESS: 결제 완료 → 취소 가능 (보통 환불 API에 가까움)
    - ❌ FAIL: 이미 실패한 결제 → 취소 불가능
    - ❌ CANCEL: 이미 취소됨 → 재취소 불가능
    """
    payment = _FAKE_PAYMENT_DB.get(transaction_id)
    if not payment:
        return {
            "status": PaymentStatus.FAIL.value,
            "transaction_id": transaction_id,
            "message": "결제 내역을 찾을 수 없습니다.",
        }

    current_status = payment["status"]

    if current_status == PaymentStatus.CANCEL.value:
        return {
            "status": PaymentStatus.CANCEL.value,
            "transaction_id": transaction_id,
            "message": "이미 취소된 결제입니다.",
        }

    if current_status == PaymentStatus.FAIL.value:
        return {
            "status": PaymentStatus.FAIL.value,
            "transaction_id": transaction_id,
            "message": "실패한 결제는 취소할 수 없습니다.",
        }

    # ✅ PENDING 또는 SUCCESS일 때만 취소 처리
    payment["status"] = PaymentStatus.CANCEL.value
    return {
        "status": PaymentStatus.CANCEL.value,
        "transaction_id": transaction_id,
        "message": (
            "결제가 확정되기 전 취소되었습니다."
            if current_status == PaymentStatus.PENDING.value
            else "결제가 완료되었지만 취소 처리되었습니다."
        ),
    }


def get_payment_status(transaction_id: str) -> Optional[dict]:
    """
    📡 결제 상태 조회
    - 현재 상태를 반환 (PENDING / SUCCESS / FAIL / CANCEL)
    - 실 PG에서 결제 단건 조회 API 역할과 동일
    """
    payment = _FAKE_PAYMENT_DB.get(transaction_id)
    if not payment:
        return None

    return {
        "status": payment["status"],
        "transaction_id": transaction_id,
        "message": f"현재 결제 상태: {payment['status']}",
    }
