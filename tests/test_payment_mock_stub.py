# tests/test_payment_mock_stub.py

import os
import sys
from unittest.mock import Mock
import pytest

# --- make project root importable ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway


def test_pay_late_fees_success_with_mock(monkeypatch):
    import services.library_service as lib

    # stub late-fee calc → always has something to pay
    def fake_fee(patron_id, book_id):
        return {"fee_amount": 5.0, "days_overdue": 3}

    # stub book lookup → book must exist, otherwise library_service will fail
    def fake_get_book_by_id(book_id):
        return {"id": book_id, "title": "Stub Book"}

    monkeypatch.setattr(lib, "calculate_late_fee_for_book", fake_fee)
    monkeypatch.setattr(lib, "get_book_by_id", fake_get_book_by_id)

    # mock external gateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_001", "Payment accepted")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert ok is True
    assert "Payment successful" in msg
    assert txn == "txn_001"
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_gateway_failure(monkeypatch):
    import services.library_service as lib

    def fake_fee(patron_id, book_id):
        return {"fee_amount": 5.0, "days_overdue": 2}

    def fake_get_book_by_id(book_id):
        return {"id": book_id, "title": "Stub Book"}

    monkeypatch.setattr(lib, "calculate_late_fee_for_book", fake_fee)
    monkeypatch.setattr(lib, "get_book_by_id", fake_get_book_by_id)

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Insufficient funds")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert ok is False
    assert "Payment failed" in msg
    assert txn is None


def test_pay_late_fees_gateway_exception(monkeypatch):
    import services.library_service as lib

    def fake_fee(patron_id, book_id):
        return {"fee_amount": 5.0, "days_overdue": 2}

    def fake_get_book_by_id(book_id):
        return {"id": book_id, "title": "Stub Book"}

    monkeypatch.setattr(lib, "calculate_late_fee_for_book", fake_fee)
    monkeypatch.setattr(lib, "get_book_by_id", fake_get_book_by_id)

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network down")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert ok is False
    assert "Payment processing error" in msg
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_stub_fee(monkeypatch):
    import services.library_service as lib

    def fake_fee(*args, **kwargs):
        return {"fee_amount": 10.0, "days_overdue": 5}

    def fake_get_book_by_id(book_id):
        return {"id": book_id, "title": "Stub Book"}

    monkeypatch.setattr(lib, "calculate_late_fee_for_book", fake_fee)
    monkeypatch.setattr(lib, "get_book_by_id", fake_get_book_by_id)

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_stub", "OK")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert ok
    assert txn == "txn_stub"
    mock_gateway.process_payment.assert_called_once()


def test_refund_late_fee_success():
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund successful")

    ok, msg = refund_late_fee_payment("txn_abc", 5.0, mock_gateway)

    assert ok
    assert "Refund successful" in msg
    mock_gateway.refund_payment.assert_called_once_with("txn_abc", 5.0)


def test_refund_late_fee_fail():
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Denied")

    ok, msg = refund_late_fee_payment("txn_abc", 5.0, mock_gateway)

    assert not ok
    assert "Refund failed" in msg

def test_pay_late_fees_invalid_patron_id():
    ok, msg, txn = pay_late_fees("abc", 1)
    assert ok is False
    assert "invalid patron" in msg.lower()

def test_pay_late_fees_no_late_fee(monkeypatch):
    mock_gateway = Mock()
    import services.library_service as svc
    monkeypatch.setattr(svc, "calculate_late_fee_for_book", lambda *_: {"fee_amount": 0.0})
    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    assert ok is False
    assert "no late fees" in msg.lower()

def test_refund_too_large_amount():
    ok, msg = refund_late_fee_payment("txn_123", 100.0)
    assert ok is False
    assert "exceeds" in msg.lower()