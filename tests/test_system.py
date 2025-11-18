# tests/test_system.py

import pytest
from app import create_app


@pytest.fixture
def client():
    """
    Create a Flask test client for system / integration tests.
    """
    app = create_app()
    app.config.update(
        TESTING=True, 
    )

    with app.test_client() as client:
        yield client

def test_catalog_page_loads(client):
    """
    System test: catalog page should be reachable and return HTTP 200.
    """
    response = client.get("/catalog")
    assert response.status_code == 200
    assert response.data  # response body should not be empty

def test_api_search_returns_json(client):
    """
    System test: /api/search should return JSON with a results list.
    """
    response = client.get("/api/search?q=great&type=title")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert "count" in data
    assert isinstance(data["results"], list)


def test_api_late_fee_returns_fee_info(client):
    """
    System test: /api/late_fee/<patron>/<book> should return fee information.
    """
    response = client.get("/api/late_fee/123456/1")
    assert response.status_code in (200, 404, 400, 500)

    data = response.get_json()
    assert isinstance(data, dict)
    assert "fee_amount" in data

