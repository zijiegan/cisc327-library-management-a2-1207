# tests/test_coverage_extra.py
from types import SimpleNamespace

import services.library_service as svc


def test_search_falls_back_to_memory_when_db_empty(monkeypatch):
    # force DB path to return empty -> should seed in-memory catalog
    monkeypatch.setattr(svc, "get_all_books", lambda: [])
    results = svc.search_books_in_catalog("great", "title")
    # in-memory seed has "The Great Gatsby"
    assert any("great" in b["title"].lower() for b in results)


def test_add_book_falls_back_to_memory_when_db_insert_fails(monkeypatch):
    # make insert_book raise to trigger memory fallback
    def boom(*args, **kwargs):
        raise Exception("DB down")

    monkeypatch.setattr(svc, "insert_book", boom)

    ok, msg = svc.add_book_to_catalog(
        "Fallback Book", "Fallback Author", "9999999999999", 1
    )
    assert ok is True
    assert "successfully added" in msg.lower()


def test_pay_late_fees_creates_gateway_when_none(monkeypatch):
    # fake late-fee info
    monkeypatch.setattr(
        svc, "calculate_late_fee_for_book",
        lambda patron_id, book_id: {"fee_amount": 3.5}
    )
    # fake book
    monkeypatch.setattr(
        svc, "get_book_by_id",
        lambda book_id: {"id": book_id, "title": "Dummy"}
    )

    # dummy gateway to capture call
    class DummyGateway:
        def __init__(self):
            self.called = False

        def process_payment(self, **kwargs):
            self.called = True
            return True, "txn_dummy", "ok"

    # patch the class name inside library_service
    monkeypatch.setattr(svc, "PaymentGateway", DummyGateway)

    ok, msg, txn = svc.pay_late_fees("123456", 1, payment_gateway=None)
    assert ok is True
    assert txn == "txn_dummy"


def test_refund_late_fee_handles_gateway_failure(monkeypatch):
    # create a fake gateway that fails to refund
    fake_gateway = SimpleNamespace(
        refund_payment=lambda txn, amt: (False, "gateway down")
    )

    ok, msg = svc.refund_late_fee_payment("txn_123", 5.0, fake_gateway)
    assert ok is False
    assert "gateway down" in msg.lower()
