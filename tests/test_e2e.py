# tests/test_e2e.py

from playwright.sync_api import Page, expect


def test_catalog_page_e2e(page: Page):
    """
    E2E test: open the catalog page in a real browser and
    check that the page loads and shows some expected text.
    """
    page.goto("http://127.0.0.1:5000/catalog", wait_until="networkidle")

    # Check that the page body contains some text related to the catalog.
    # If your page shows a different heading, adjust the text below.
    expect(page.locator("body")).to_contain_text("Library")

def test_search_page_e2e(page: Page):
    """
    E2E test: open the search page with query and check that
    the page shows something related to the search.
    """
    page.goto("http://127.0.0.1:5000/search?q=great&type=title", wait_until="networkidle")

    body = page.locator("body")
    expect(body).to_contain_text("Great")

