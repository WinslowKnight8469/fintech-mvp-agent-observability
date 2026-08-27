from order_agent import review_payment


def test_review_payment_uses_default_flag(monkeypatch):
    monkeypatch.setattr("order_agent.flag_value", lambda key, default_value: default_value)
    monkeypatch.setattr("order_agent.report_metric", lambda name, value, agent: {})
    assert review_payment(42) == "approved"
