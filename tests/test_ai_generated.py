# tests/test_ai_generated.py
"""
AI-generated smoke tests for R1, R6, R7.
- R1: add_book_to_catalog - happy path + minimal validation
- R6: search_books_in_catalog - should find the book we just added
- R7: patron status report - basic structure and non-negative numbers

These tests are intentionally light-weight and self-cleaning. They only rely on
public functions in library_service, and remove any inserted book rows by ISBN.
"""

import re
import time
import sqlite3
import pytest

import services.library_service as svc
from services.payment_service import PaymentGateway


# ---------- helpers ----------

def _find_func(candidates):
    """Return the first function that exists in library_service from candidates."""
    for name in candidates:
        if hasattr(svc, name):
            return getattr(svc, name)
    return None


def _unique_isbn() -> str:
    """Return a 13-digit string that is very unlikely to collide."""
    # prefix '8' + 12 digits from time ns
    return ("8" + str(time.time_ns()))[:13]


def _cleanup_isbn(isbn: str):
    """Delete the book row by ISBN to keep DB clean (direct sqlite for cleanup only)."""
    try:
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE isbn = ?", (isbn,))
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ---------- R1: Book Catalog Management ----------

@pytest.mark.order(1)
def test_r1_add_book_happy_path_ai():
    add_book = _find_func(["add_book_to_catalog", "add_book"])
    if not add_book:
        pytest.skip("add_book_to_catalog not found in library_service")

    isbn = _unique_isbn()
    try:
        ok, msg = add_book("AI Unit Test Book", "AI Bot", isbn, 2)
        assert ok is True
        assert isinstance(msg, str) and msg  # non-empty message

        # sanity check: record exists now
        get_by_isbn = _find_func(["get_book_by_isbn"])
        if get_by_isbn:
            row = get_by_isbn(isbn)
            assert row, "Book should be retrievable right after insert"
            # accept either dict-like or row-like
            text = str(row)
            assert "AI Unit Test Book" in text and isbn in text
    finally:
        _cleanup_isbn(isbn)


@pytest.mark.order(2)
def test_r1_add_book_validation_ai():
    add_book = _find_func(["add_book_to_catalog", "add_book"])
    if not add_book:
        pytest.skip("add_book_to_catalog not found in library_service")

    # invalid: empty title
    ok, msg = add_book("", "Someone", _unique_isbn(), 1)
    assert ok is False
    assert "title" in msg.lower()

    # invalid: isbn length
    ok, msg = add_book("T", "A", "12345", 1)
    assert ok is False
    assert "isbn" in msg.lower()

    # invalid: copies <= 0
    ok, msg = add_book("T", "A", _unique_isbn(), 0)
    assert ok is False
    assert ("copy" in msg.lower()) or ("positive" in msg.lower())


# ---------- R6: Search Functionality ----------

@pytest.mark.order(3)
def test_r6_search_finds_inserted_book_ai():
    add_book = _find_func(["add_book_to_catalog", "add_book"])
    search = _find_func(["search_books_in_catalog", "search_books", "find_books"])
    if not add_book or not search:
        pytest.skip("search_books_in_catalog or add_book_to_catalog not found")

    isbn = _unique_isbn()
    title = "AI Search Smoke Title"
    author = "Unit Tester"

    try:
        ok, _ = add_book(title, author, isbn, 1)
        assert ok is True

        # Search by title (partial, case-insensitive expected by R6)
        results = search("search smoke", "title")
        assert isinstance(results, list)
        joined = " | ".join(map(str, results)).lower()
        assert "ai search smoke title".lower() in joined
        assert isbn in joined
    finally:
        _cleanup_isbn(isbn)


# ---------- R7: Patron Status Report ----------

@pytest.mark.order(4)
def test_r7_patron_status_basic_shape_ai():
    patron_fn = _find_func([
        "get_patron_status", "patron_status_report", "patron_status",
        "get_patron_status_report"
    ])
    if not patron_fn:
        pytest.skip("patron status API not found in library_service")

    # use a known demo patron id frequently present in sample data
    patron_id = "123456"
    report = patron_fn(patron_id)

    # Basic shape + fields
    assert isinstance(report, dict)
    # allow flexible key naming; check common ones
    keys = set(map(str.lower, report.keys()))
    # date/action are often present
    assert "date" in keys or "generated" in " ".join(keys)
    # totals / fees info
    assert any(k in keys for k in ["total_late_fees", "total fees", "late_fees", "fees"])
    # borrowed list presence
    assert any("borrow" in k for k in keys)

    # numeric fields, non-negative
    def _num(v):
        try:
            return float(v)
        except Exception:
            return None

    nums = [_num(report.get(k)) for k in report.keys()]
    for v in filter(lambda x: x is not None, nums):
        assert v >= 0
