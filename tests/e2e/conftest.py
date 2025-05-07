import sqlite3
import time
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def wait_for_docker():
    time.sleep(2.5)
    yield


@pytest.fixture(autouse=True)
def clean_db(cursor):
    for table in ("events_eventmodel", "events_eventlog"):
        cursor.execute(f"DELETE FROM {table}")
    cursor.connection.commit()
    yield


@pytest.fixture
def cursor() -> sqlite3.Cursor:
    return sqlite3.connect(
        Path(__file__).resolve().parent / "django/src/db.sqlite3"
    ).cursor()
