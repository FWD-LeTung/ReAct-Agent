# calculate.py

from typing import Tuple, Dict


def calculate_simple_interest(amount: float, rate: float, duration: int) -> Tuple[float, float]:
    """
    Lãi đơn
    amount: số tiền (VND)
    rate: %/năm
    duration: tháng
    """
    interest = amount * (rate / 100) * (duration / 12)
    total = amount + interest
    return interest, total


def calculate_compound_interest(amount: float, rate: float, duration: int, n: int = 1) -> Tuple[float, float]:
    """
    Lãi kép
    n: số lần nhập gốc mỗi năm
    """
    t = duration / 12
    total = amount * (1 + (rate / 100) / n) ** (n * t)
    interest = total - amount
    return interest, total


def calculate_early_withdraw(amount: float, withdraw_time: int, rate: float = 0.2) -> Tuple[float, float]:
    """
    Rút trước hạn → lãi không kỳ hạn (~0.2%)
    """
    interest = amount * (rate / 100) * (withdraw_time / 12)
    total = amount + interest
    return interest, total


def calculate_partial_withdraw(
    total_amount: float,
    withdraw_amount: float,
    withdraw_time: int,
    duration: int,
    rate: float
) -> Dict:
    """
    Rút một phần:
    - phần rút → lãi không kỳ hạn
    - phần còn lại → giữ lãi kỳ hạn
    """

    remaining_amount = total_amount - withdraw_amount

    # phần rút
    interest_withdraw, total_withdraw = calculate_early_withdraw(
        withdraw_amount, withdraw_time
    )

    # phần còn lại
    interest_remaining, total_remaining = calculate_simple_interest(
        remaining_amount, rate, duration
    )

    return {
        "withdraw_part": {
            "amount": withdraw_amount,
            "interest": interest_withdraw,
            "total": total_withdraw
        },
        "remaining_part": {
            "amount": remaining_amount,
            "interest": interest_remaining,
            "total": total_remaining
        },
        "total_interest": interest_withdraw + interest_remaining,
        "total_amount": total_withdraw + total_remaining
    }


def calculate(
    amount: float,
    rate: float,
    duration: int,
    interest_type: str = "simple",
    withdraw_time: int = None,
    withdraw_amount: float = None
) -> Dict:
    """
    Hàm tổng (main API)
    """

    # 🔴 Rút trước hạn toàn bộ
    if withdraw_time is not None and withdraw_amount is None:
        interest, total = calculate_early_withdraw(amount, withdraw_time)
        return {
            "type": "early_withdraw",
            "interest": interest,
            "total": total
        }

    # 🟡 Rút một phần
    if withdraw_amount is not None:
        return calculate_partial_withdraw(
            amount,
            withdraw_amount,
            withdraw_time,
            duration,
            rate
        )

    # 🟢 Bình thường
    if interest_type == "compound":
        interest, total = calculate_compound_interest(amount, rate, duration)
    else:
        interest, total = calculate_simple_interest(amount, rate, duration)

    return {
        "type": "normal",
        "interest": interest,
        "total": total
    }


# 🧪 Test nhanh
if __name__ == "__main__":
    # Case 1: bình thường
    print(calculate(100_000_000, 6.0, 6))

    # Case 2: rút sớm
    print(calculate(100_000_000, 6.0, 6, withdraw_time=2))

    # Case 3: partial withdraw
    print(calculate(100_000_000, 6.0, 6, withdraw_time=2, withdraw_amount=40_000_000))
