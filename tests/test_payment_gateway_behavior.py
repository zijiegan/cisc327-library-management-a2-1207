import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

def test_pay_late_fees_success():
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_001", "Payment ok")
    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    assert ok is True
    assert "successful" in msg.lower()
    assert txn.startswith("txn_")

def test_pay_late_fees_fail_gateway_error():
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network error")
    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    assert ok is False
    assert "error" in msg.lower()

def test_refund_success():
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund complete")
    ok, msg = refund_late_fee_payment("txn_123", 5.0, mock_gateway)
    assert ok is True
    assert "refund" in msg.lower() or "complete" in msg.lower()

def test_refund_invalid_transaction():
    ok, msg = refund_late_fee_payment("bad_id", 5.0)
    assert ok is False
    assert "invalid transaction" in msg.lower()

def test_real_gateway_process_payment(monkeypatch):
    """Use monkeypatch to stub out requests.post so we don't hit a real API."""
    import requests
    class DummyResponse:
        def __init__(self, ok=True, status_code=200):
            self.ok = ok
            self.status_code = status_code
            self.text = "OK"
        def json(self):
            return {"id": "txn_999"}

    monkeypatch.setattr(requests, "post", lambda *a, **kw: DummyResponse())
    gateway = PaymentGateway()
    ok, txn, msg = gateway.process_payment("123456", 5.0, "Test payment")
    assert ok is True
    assert txn.startswith("txn_")
def test_real_gateway_refund_payment(monkeypatch):
    import requests
    class DummyResponse:
        def __init__(self):
            self.ok = True
            self.status_code = 200
            self.text = "Refund OK"
        def json(self):
            return {"status": "done"}
    monkeypatch.setattr(requests, "post", lambda *a, **kw: DummyResponse())

    gateway = PaymentGateway()
    ok, msg = gateway.refund_payment("txn_999", 5.0)
    assert ok is True
    assert "refund" in msg.lower() or "done" in msg.lower()
