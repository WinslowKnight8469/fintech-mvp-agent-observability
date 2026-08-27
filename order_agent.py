"""Runnable day-one observability example for a payment review agent."""
import sys

from infrai_observability import capture_exception, flag_value, report_metric


def review_payment(amount: float) -> str:
    """Apply a flag, record latency-like work, and capture an agent failure."""
    agent = "payment-review-agent"
    enabled = flag_value("payment-review-v2", False)
    report_metric("payment_review_started", 1, agent)
    if amount <= 0:
        error = ValueError("payment amount must be positive")
        capture_exception(error, agent, "validate-payment")
        raise error
    decision = "v2-approved" if enabled else "approved"
    report_metric("payment_review_completed", 1, agent)
    return decision


if __name__ == "__main__":
    amount = float(sys.argv[1]) if len(sys.argv) > 1 else 42.0
    print(review_payment(amount))
