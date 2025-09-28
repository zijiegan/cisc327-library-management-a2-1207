# tests/conftest.py
import os
import sqlite3
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Always start with a clean database for tests
    if os.path.exists("library.db"):
        os.remove("library.db")

    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        isbn TEXT UNIQUE,
        total_copies INTEGER,
        available_copies INTEGER
    )
    """)

    seed = [
        ("1984", "George Orwell", "9780451524935", 5, 5),
        ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "9780747532699", 5, 5),
        ("To Kill a Mockingbird", "Harper Lee", "9780061120084", 5, 5),
    ]
    for t, a, i, tot, ava in seed:
        c.execute(
            "INSERT OR IGNORE INTO books (title, author, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
            (t, a, i, tot, ava)
        )
    conn.commit()
    conn.close()
