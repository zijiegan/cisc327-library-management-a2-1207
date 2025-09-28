import pytest
import library_service as svc

def test_add_book_valid():
    """Valid book should be added successfully"""
    success, message = svc.add_book_to_catalog("Book A", "Author A", "1234567890123", 3)
    assert success is True
    assert "successfully added" in message.lower()

def test_add_book_missing_title():
    """Book without title should fail"""
    success, message = svc.add_book_to_catalog("", "Author A", "1234567890123", 3)
    assert success is False
    assert "title" in message.lower()

def test_add_book_long_title():
    """Book with title over 200 chars should fail"""
    long_title = "A" * 201
    success, message = svc.add_book_to_catalog(long_title, "Author A", "1234567890123", 3)
    assert success is False
    assert "title" in message.lower()

def test_add_book_invalid_isbn():
    """ISBN not 13 digits should fail"""
    success, message = svc.add_book_to_catalog("Book B", "Author B", "12345", 3)
    assert success is False
    assert "isbn" in message.lower()

def test_add_book_invalid_copies():
    """Total copies not positive should fail"""
    success, message = svc.add_book_to_catalog("Book C", "Author C", "1234567890123", 0)
    assert success is False
    assert "copies" in message.lower()
