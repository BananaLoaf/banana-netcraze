import os

import pytest


@pytest.fixture
def credentials():
    username = os.environ.get("TEST_USERNAME")
    password = os.environ.get("TEST_PASSWORD")
    if not username or not password:
        pytest.skip("Env vars TEST_USERNAME and TEST_PASSWORD not set")
    return {"username": username, "password": password}
