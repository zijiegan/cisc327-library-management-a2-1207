# tests/test_late_fee.py
import pytest
import library_service as svc

def test_late_fee_no_overdue():
    """Returned within 14 days: no fee"""
    result = svc.calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)
    assert "fee_amount" in result and "days_overdue" in result
    assert result["days_overdue"] == 0
    assert float(result["fee_amount"]) == 0.0

def test_late_fee_3_days_overdue():
    """3 days overdue: $0.50/day => $1.50"""
    result = svc.calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)
    # Expect 3 days and $1.50 (0.5 * 3)
    assert result.get("days_overdue", -1) == 3
    assert round(float(result.get("fee_amount", -1.0)), 2) == 1.50

def test_late_fee_10_days_overdue():
    """10 days overdue: 7*0.5 + 3*1.0 = $6.50"""
    result = svc.calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)
    assert result.get("days_overdue", -1) == 10
    assert round(float(result.get("fee_amount", -1.0)), 2) == 6.50

def test_late_fee_cap_at_15():
    """Large overdue should be capped at $15.00"""
    result = svc.calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)
    assert result.get("days_overdue", -1) > 30  # arbitrary large overdue
    assert round(float(result.get("fee_amount", -1.0)), 2) == 15.00

def test_late_fee_missing_record():
    """If there is no borrow record, the API should report it clearly"""
    result = svc.calculate_late_fee_for_book("123456", 999)
    # Expect either an error status or a specific message in 'status'
    assert isinstance(result, dict)
    assert "status" in result
    assert "not found" in result["status"].lower() or "no record" in result["status"].lower()
