import os
import sqlite3
import sys
from pathlib import Path

import pytest

SERVER_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER_ROOT))

from app import app as flask_app, get_db_connection

@pytest.fixture(scope="session")
def app():
    # Provide the Flask app for testing
    yield flask_app

@pytest.fixture(scope="session")
def client(app):
    # Flask test client
    return app.test_client()

@pytest.fixture(scope="function")
def db_connection():
    """
    Provides a DB connection for tests. Rollback any changes after each test.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    yield conn, cursor
    conn.rollback()
    cursor.close()
    conn.close()

@pytest.fixture(scope="function")
def create_sample_book(db_connection):
    """
    Fixture to create a sample book for testing update/delete/fetch.
    Returns the inserted book id.
    """
    conn, cursor = db_connection
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost, edition) VALUES (?, ?, ?, ?, ?)",
        ("TestPub", "TestBook", "2025-01-01", 50.0, "1st")
    )
    book_id = cursor.lastrowid
    conn.commit()
    yield book_id
    cursor.execute("DELETE FROM book WHERE id=?", (book_id,))
    conn.commit()
