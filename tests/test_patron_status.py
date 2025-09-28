# tests/test_patron_status.py
import pytest
import library_service as svc

def test_patron_status_basic_structure():
    """Report should be a dict with required top-level fields"""
    report = svc.get_patron_status_report("123456")
    assert isinstance(report, dict)
    for key in ["current_borrowed", "total_late_fees", "borrowed_count", "history"]:
        assert key in report

def test_patron_status_current_borrowed_items_have_due_dates():
    """Each current borrowed item should include title and due_date"""
    report = svc.get_patron_status_report("123456")
    assert isinstance(report, dict)
    items = report.get("current_borrowed", [])
    assert isinstance(items, list)
    # expect at least one item in realistic scenario
    assert len(items) >= 1
    assert all("title" in it and "due_date" in it for it in items)

def test_patron_status_total_late_fees_is_number_with_two_decimals():
    """Total late fees should be numeric and formatted with 2 decimals"""
    report = svc.get_patron_status_report("123456")
    assert isinstance(report, dict)
    fees = float(report.get("total_late_fees", -1))
    assert fees >= 0.0
    # 2-decimal formatting check by string
    assert f"{fees:.2f}" == str(report.get("total_late_fees"))

def test_patron_status_borrowed_count_matches_length():
    """borrowed_count should match the length of current_borrowed"""
    report = svc.get_patron_status_report("123456")
    current = report.get("current_borrowed", [])
    count = report.get("borrowed_count", -1)
    assert isinstance(current, list)
    assert isinstance(count, int)
    assert count == len(current)

def test_patron_status_history_entries_have_dates_and_actions():
    """History entries should indicate borrow/return actions and timestamps"""
    report = svc.get_patron_status_report("123456")
    history = report.get("history", [])
    assert isinstance(history, list)
    assert len(history) >= 1
    for entry in history:
        assert "action" in entry  # e.g., "borrow" or "return"
        assert "timestamp" in entry
