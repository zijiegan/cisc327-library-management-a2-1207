# tests/test_search_books.py
import pytest
import services.library_service as svc
from services.payment_service import PaymentGateway

def test_search_by_title_partial_case_insensitive():
    """Title partial, case-insensitive should return matches"""
    results = svc.search_books_in_catalog(search_term="great", search_type="title")
    assert isinstance(results, list)
    assert any("great gatsby" in b.get("title", "").lower() for b in results)

def test_search_by_author_partial_case_insensitive():
    """Author partial, case-insensitive should return matches"""
    results = svc.search_books_in_catalog(search_term="lee", search_type="author")
    assert isinstance(results, list)
    assert any("harper lee" in b.get("author", "").lower() for b in results)

def test_search_by_isbn_exact_match():
    """ISBN must be exact-match"""
    results = svc.search_books_in_catalog(search_term="9780451524935", search_type="isbn")
    assert isinstance(results, list)
    assert any(b.get("isbn") == "9780451524935" for b in results)

def test_search_invalid_type_returns_empty_or_error():
    """Unsupported search type should be handled (empty list or error)"""
    results = svc.search_books_in_catalog(search_term="anything", search_type="publisher")
    assert isinstance(results, list)
    # Either handled as empty result or validated; expecting empty here
    assert len(results) == 0

def test_search_empty_query_returns_all_or_empty():
    """Empty query should return either all books (catalog) or empty; decide a consistent policy"""
    results = svc.search_books_in_catalog(search_term="", search_type="title")
    assert isinstance(results, list)
    # Choose one expectation; here we expect empty for A1
    assert len(results) == 0
