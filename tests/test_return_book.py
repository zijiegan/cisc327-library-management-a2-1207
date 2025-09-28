# tests/test_return_book.py
import pytest
import library_service as svc

def test_return_success(monkeypatch):
    """Happy path: book is returned, availability updated, return date recorded"""
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: {"id": book_id, "title": "Clean Code", "available_copies": 0})
    # Pretend there is a valid borrow record and DB ops succeed
    monkeypatch.setattr(svc, "update_borrow_record_return_date", lambda patron_id, book_id, return_date: True)
    monkeypatch.setattr(svc, "update_book_availability", lambda book_id, delta: True)

    success, message = svc.return_book_by_patron("123456", 1)
    assert success is True
    assert "returned" in message.lower()

def test_return_invalid_patron_id():
    """Invalid patron id should be rejected first"""
    success, message = svc.return_book_by_patron("12A456", 1)
    assert success is False
    assert "patron" in message.lower()

def test_return_book_not_found(monkeypatch):
    """Returning a non-existing book should fail"""
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: None)
    success, message = svc.return_book_by_patron("123456", 999)
    assert success is False
    assert "book not found" in message.lower() or "book" in message.lower()

def test_return_not_borrowed_by_patron(monkeypatch):
    """If the patron never borrowed the book, it should fail with a clear message"""
    # Simulate: DB says no matching active borrow record
    def fake_update_return(patron_id, book_id, return_date):
        return False
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: {"id": book_id, "title": "Demo", "available_copies": 0})
    monkeypatch.setattr(svc, "update_borrow_record_return_date", fake_update_return)

    success, message = svc.return_book_by_patron("123456", 1)
    assert success is False
    assert "not borrowed" in message.lower() or "no record" in message.lower()

def test_return_db_failure_on_availability(monkeypatch):
    """DB failure when increasing availability should be reported"""
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: {"id": book_id, "title": "Demo", "available_copies": 0})
    monkeypatch.setattr(svc, "update_borrow_record_return_date", lambda patron_id, book_id, return_date: True)
    monkeypatch.setattr(svc, "update_book_availability", lambda book_id, delta: False)

    success, message = svc.return_book_by_patron("123456", 1)
    assert success is False
    assert "database error" in message.lower()
