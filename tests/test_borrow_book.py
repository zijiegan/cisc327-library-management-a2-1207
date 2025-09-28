# tests/test_borrow_book.py
import pytest
import library_service as svc

# Helpers
def make_book(book_id=1, title="Demo", available=2):
    return {
        "id": book_id,
        "title": title,
        "author": "Author",
        "isbn": "1234567890123",
        "total_copies": max(available, 2),
        "available_copies": available,
    }

def test_borrow_success(monkeypatch):
    # Arrange: stub DB functions to simulate a happy path
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: make_book(book_id, "Clean Code", 2))
    monkeypatch.setattr(svc, "get_patron_borrow_count", lambda patron_id: 0)
    monkeypatch.setattr(svc, "insert_borrow_record", lambda patron_id, book_id, borrow_date, due_date: True)
    monkeypatch.setattr(svc, "update_book_availability", lambda book_id, delta: True)

    # Act
    success, message = svc.borrow_book_by_patron("123456", 1)

    # Assert
    assert success is True
    assert "successfully borrowed" in message.lower()

def test_borrow_invalid_patron_id(monkeypatch):
    # Any DB calls should not happen; patron id fails first
    success, message = svc.borrow_book_by_patron("12A456", 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_borrow_book_not_found(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: None)
    success, message = svc.borrow_book_by_patron("123456", 999)
    assert success is False
    assert "book not found" in message.lower()

def test_borrow_unavailable_book(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: make_book(book_id, "Sold Out", 0))
    success, message = svc.borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not available" in message.lower()

def test_borrow_over_limit(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: make_book(book_id, "Any", 2))
    # Business rule: max 5 books; current count 6 should be rejected
    monkeypatch.setattr(svc, "get_patron_borrow_count", lambda patron_id: 6)
    success, message = svc.borrow_book_by_patron("123456", 1)
    assert success is False
    assert "maximum borrowing limit" in message.lower()

def test_borrow_db_failure_on_update(monkeypatch):
    # Insert succeeds but availability update fails -> should report DB error
    monkeypatch.setattr(svc, "get_book_by_id", lambda book_id: make_book(book_id, "Any", 2))
    monkeypatch.setattr(svc, "get_patron_borrow_count", lambda patron_id: 0)
    monkeypatch.setattr(svc, "insert_borrow_record", lambda patron_id, book_id, borrow_date, due_date: True)
    monkeypatch.setattr(svc, "update_book_availability", lambda book_id, delta: False)

    success, message = svc.borrow_book_by_patron("123456", 1)
    assert success is False
    assert "database error" in message.lower()